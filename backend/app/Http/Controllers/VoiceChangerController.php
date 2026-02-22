<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\Storage;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Auth;
use Illuminate\Support\Facades\Log;

use App\Services\RunpodService;
use App\Services\StorageService;

class VoiceChangerController extends Controller
{
    protected $runpod;
    protected $storage;

    public function __construct(RunpodService $runpod, StorageService $storage)
    {
        $this->runpod = $runpod;
        $this->storage = $storage;
    }

    /**
     * Step 1: Voice Initialization
     * Upload audio dan ambil ID embedding dari Python
     */
    public function initializeVoice(Request $request)
    {
        $request->validate([
            'audio' => 'required|file|max:524288', // 512MB
        ]);

        $audio = $request->file('audio');

        // SIMPAN: Agar bisa dipakai buat training nanti (Fallback)
        $audio->store('references', 'public');

        $baseUrl = env('AI_GENERATE_URL', 'http://localhost:5000');

        try {
            // Ditambah timeout karena file 300MB+ butuh waktu kirim
            $response = Http::timeout(300)->attach(
                'audio',
                file_get_contents($audio->getRealPath()),
                'ref.wav'
            )->post("{$baseUrl}/extract_speaker");

            if ($response->successful()) {
                $data = $response->json();
                return response()->json([
                    'success' => true,
                    'speaker_id' => $data['speaker_id'],
                    'message' => 'Profile suara berhasil diekstrak dan disimpan di server.'
                ]);
            }

            return response()->json(['error' => 'Gagal memproses suara: ' . $response->body()], 500);
        } catch (\Exception $e) {
            Log::error("❌ INITIALIZE ERROR: " . $e->getMessage());
            return response()->json(['error' => 'Server AI Offline / Timeout'], 500);
        }
    }

    /**
     * Step 2: Voice Generation
     * Menggunakan speaker_id yang sudah disimpan
     */
    public function clone(Request $request)
    {
        // Validasi input
        $request->validate([
            'text' => 'required|string|max:500',
            'speaker_id' => 'nullable|string', // ID dari Step 1
            'audio' => 'nullable|file|max:524288', // Support fallback upload langsung
            'speed' => 'nullable|numeric|min:0.5|max:2.0',
        ]);

        $text = $request->input('text');
        $speakerId = $request->input('speaker_id');
        $speed = $request->input('speed', 1.0);
        $userId = Auth::check() ? Auth::id() : null;

        // Simpan data transaksi ke database (Opsional jika DB belum siap)
        $generationId = null;
        try {
            $generationId = DB::table('voice_generations')->insertGetId([
                'user_id' => $userId,
                'input_text' => $text,
                'reference_audio_path' => $request->hasFile('audio') ? $request->file('audio')->store('references', 'public') : 'using_cached_speaker',
                'status' => 'processing',
                'created_at' => now(),
                'updated_at' => now(),
            ]);
        } catch (\Exception $e) {
            // Silently fail if DB not ready
        }

        $baseUrl = env('AI_GENERATE_URL', 'http://localhost:5000');

        try {
            $postData = [
                'text' => $text,
                'speed' => $speed,
                'speaker_id' => $speakerId
            ];

            $requestChain = Http::timeout(300);

            if ($request->hasFile('audio')) {
                $requestChain->attach(
                    'audio',
                    file_get_contents($request->file('audio')->getRealPath()),
                    'ref.wav'
                );
            }

            $response = $requestChain->post("{$baseUrl}/clone", $postData);

            if ($response->successful() && strlen($response->body()) > 0) {
                $filename = 'generated/' . uniqid() . '.wav';
                Storage::disk('public')->put($filename, $response->body());

                // Update status sukses ke DB
                if ($generationId) {
                    try {
                        DB::table('voice_generations')->where('id', $generationId)->update([
                            'result_audio_path' => $filename,
                            'status' => 'completed',
                            'updated_at' => now(),
                        ]);
                    } catch (\Exception $e) {
                    }
                }

                // Return both binary audio and persistent URL
                $fileUrl = asset('storage/' . $filename);

                return response($response->body(), 200)
                    ->header('Content-Type', 'audio/wav')
                    ->header('X-Voice-Engine', 'xtts-v2')
                    ->header('X-File-URL', $fileUrl);
            }

            $pythonError = $response->body() ?: 'Unknown AI error';
            if ($generationId) {
                try {
                    DB::table('voice_generations')->where('id', $generationId)->update(['status' => 'failed']);
                } catch (\Exception $e) {
                }
            }

            return response()->json(['error' => 'AI Engine Error: ' . $pythonError], 500);
        } catch (\Exception $e) {
            return response()->json(['error' => 'AI Server Offline'], 500);
        }
    }

    public function startTraining(Request $request)
    {
        try {
            Log::info("DEBUG: Memulai StartTraining - Menunggu upload file...");

            // 1. CARI FILE dari request
            $audioFile = $request->file('audio') ?? $request->file('file') ?? collect($request->allFiles())->first();

            $datasetPath = null;

            if ($audioFile) {
                // VALIDASI: Izinkan file besar hingga 512MB
                $request->validate([
                    'audio' => 'nullable|file|max:524288',
                    'file' => 'nullable|file|max:524288'
                ]);

                // Skema A: Ada file yang di-upload saat ini
                $tempPath = $audioFile->store('temp_audio', 'public');
                $fullLocalPath = storage_path('app/public/' . $tempPath);

                $datasetPath = "training/raw/user_" . time() . "_" . $audioFile->getClientOriginalName();
                Log::info("DEBUG: Uploading file baru ke R2: $datasetPath");

                $this->storage->uploadToCloud($fullLocalPath, $datasetPath);
                @unlink($fullLocalPath);
            } else {
                // Skema B: Tidak ada file di request, cari file TERBESAR di folder references
                Log::info("DEBUG: Tidak ada file di request. Mencari file TERBESAR di storage references...");

                $allFiles = Storage::disk('public')->files('references');

                // Urutkan berdasarkan ukuran (paling besar di atas)
                $largestFile = collect($allFiles)->sortByDesc(function ($file) {
                    return Storage::disk('public')->size($file);
                })->first();

                if ($largestFile) {
                    $fullLocalPath = storage_path('app/public/' . $largestFile);
                    $fileSizeMB = round(Storage::disk('public')->size($largestFile) / 1024 / 1024, 2);
                    $datasetPath = "training/raw/auto_" . time() . "_" . basename($largestFile);

                    Log::info("✅ Ditemukan file besar di storage: " . basename($largestFile) . " ($fileSizeMB MB)");
                    $this->storage->uploadToCloud($fullLocalPath, $datasetPath);
                } else {
                    $contentLength = $request->getContentLength();
                    Log::error("❌ ERROR: File tidak ditemukan. Content-Length: $contentLength bytes.");
                    return response()->json([
                        'error' => 'Gagal: File audio 30 menit tidak ditemukan. Silakan upload ulang di kotak atas.'
                    ], 422);
                }
            }

            if (!$datasetPath) {
                return response()->json([
                    'error' => 'Gagal: Silakan pilih atau upload file audio terlebih dahulu.'
                ], 422);
            }

            $userId = Auth::check() ? Auth::id() : 'guest_admin';

            // 3. Memanggil RunPod Worker
            Log::info("🚀 Triggering RunPod training with path: $datasetPath");
            $response = $this->runpod->train([
                'user_id' => (string)$userId,
                'audio_path' => $datasetPath,
                'model_name' => 'premium_voice_' . time(),
                'epochs' => 100
            ]);

            return response()->json([
                'success' => true,
                'message' => 'Training Premium berhasil dipicu!',
                'data' => $response
            ]);
        } catch (\Exception $e) {
            Log::error("❌ ERROR TRAINING: " . $e->getMessage());
            return response()->json(['error' => $e->getMessage()], 500);
        }
    }

    public function engineStatus()
    {
        $engines = [
            'xtts' => [
                'url' => env('AI_GENERATE_URL', 'http://127.0.0.1:5000'),
                'name' => 'XTTS v2',
                'quality' => 'Optimization: Indonesian'
            ]
        ];

        $results = [];
        foreach ($engines as $key => $info) {
            try {
                $status = Http::timeout(2)->get("{$info['url']}/health");
                $results[$key] = array_merge($info, [
                    'available' => $status->successful(),
                    'port' => parse_url($info['url'], PHP_URL_PORT),
                    'details' => $status->json()
                ]);
            } catch (\Exception $e) {
                $results[$key] = array_merge($info, [
                    'available' => false,
                    'port' => parse_url($info['url'], PHP_URL_PORT)
                ]);
            }
        }

        return response()->json(['engines' => $results]);
    }
}
