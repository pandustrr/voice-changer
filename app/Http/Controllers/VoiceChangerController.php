<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\Storage;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Auth;

class VoiceChangerController extends Controller
{
    /**
     * Voice cloning dengan Multi-Engine support
     * Engine 1: XTTS v2 (Port 5000) - Fallback / Free
     * Engine 2: GPT-SoVITS (Port 5001) - Indonesian Native
     */
    public function clone(Request $request)
    {
        // Validasi input
        $request->validate([
            'audio' => 'required|file|max:35000', // max 35MB
            'text' => 'required|string|max:500',
            'engine' => 'nullable|in:xtts,gptsovits', // Pemilihan engine
            'reference_text' => 'nullable|string|max:500', // Teks yang diucapkan di rekaman
            'speed' => 'nullable|numeric|min:0.5|max:2.0', // Kontrol kecepatan bicara
        ]);

        $audio = $request->file('audio');
        $text = $request->input('text');
        $enginePreference = $request->input('engine', 'xtts');
        $referenceText = $request->input('reference_text', ''); // PENTING untuk kemiripan
        $speed = $request->input('speed', 1.0);

        // Gunakan Auth facade yang lebih stabil
        $userId = Auth::check() ? Auth::id() : null;

        // Simpan data transaksi ke database
        $generationId = DB::table('voice_generations')->insertGetId([
            'user_id' => $userId,
            'input_text' => $text,
            'reference_audio_path' => $audio->store('references', 'public'),
            'status' => 'processing',
            'created_at' => now(),
            'updated_at' => now(),
        ]);

        // Map base URL berdasarkan engine dari .env
        $baseUrl = $enginePreference === 'gptsovits'
            ? env('AI_GPTSOVITS_URL', 'http://localhost:5001')
            : env('AI_XTTS_URL', 'http://localhost:5000');

        try {
            // Kirim ke server Python (Timeout 300 detik)
            $postData = [
                'text' => $text,
                'speed' => $speed,
            ];

            // Kirim reference_text jika ada (untuk GPT-SoVITS)
            if (!empty($referenceText)) {
                $postData['reference_text'] = $referenceText;
            }

            $response = Http::timeout(300)->attach(
                'audio',
                file_get_contents($audio->getRealPath()),
                'ref.wav'
            )->post("{$baseUrl}/clone", $postData);

            if ($response->successful() && strlen($response->body()) > 0) {
                // Semua output sekarang dalam format WAV
                $filename = 'generated/' . uniqid() . '.wav';

                Storage::disk('public')->put($filename, $response->body());

                // Update status sukses
                DB::table('voice_generations')->where('id', $generationId)->update([
                    'result_audio_path' => $filename,
                    'status' => 'completed',
                    'updated_at' => now(),
                ]);

                return response($response->body(), 200)
                    ->header('Content-Type', 'audio/wav')
                    ->header('X-Voice-Engine', $enginePreference);
            }

            // Capture the actual error from Python
            $pythonError = $response->body() ?: 'Unknown Python error';

            // Update status gagal
            DB::table('voice_generations')->where('id', $generationId)->update([
                'status' => 'failed',
                'updated_at' => now(),
            ]);

            return response()->json([
                'error' => 'AI Engine Error: ' . $pythonError,
                'engine_used' => $enginePreference
            ], 500);
        } catch (\Exception $e) {
            return response()->json([
                'error' => 'AI Server Offline: ' . $e->getMessage(),
                'engine_attempted' => $enginePreference
            ], 500);
        }
    }

    public function engineStatus()
    {
        $engines = [
            'xtts' => [
                'url' => env('AI_XTTS_URL', 'http://localhost:5000'),
                'name' => 'XTTS v2',
                'quality' => 'Free / Good'
            ],
            'gptsovits' => [
                'url' => env('AI_GPTSOVITS_URL', 'http://localhost:5001'),
                'name' => 'GPT-SoVITS',
                'quality' => 'Indonesian Native'
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
