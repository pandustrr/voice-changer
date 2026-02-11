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
     * Engine 3: ElevenLabs (Port 5002) - Premium Quality
     */
    public function clone(Request $request)
    {
        // Validasi input
        $request->validate([
            'audio' => 'required|file|max:35000', // max 35MB
            'text' => 'required|string|max:500',
            'engine' => 'nullable|in:xtts,gptsovits,elevenlabs', // Pemilihan engine
        ]);

        $audio = $request->file('audio');
        $text = $request->input('text');
        $enginePreference = $request->input('engine', 'xtts');

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

        // Map port berdasarkan engine
        $ports = [
            'xtts' => 5000,
            'gptsovits' => 5001,
            'elevenlabs' => 5002
        ];

        $port = $ports[$enginePreference] ?? 5000;

        try {
            // Kirim ke server Python (Timeout 5 menit karena AI berat)
            $response = Http::timeout(300)->attach(
                'audio',
                file_get_contents($audio->getRealPath()),
                'ref.wav'
            )->post("http://localhost:{$port}/clone", [
                'text' => $text,
            ]);

            if ($response->successful() && strlen($response->body()) > 0) {
                // ElevenLabs output MP3, lainnya WAV. Kita simpan sesuai ekstensi respons.
                $ext = $enginePreference === 'elevenlabs' ? 'mp3' : 'wav';
                $filename = 'generated/' . uniqid() . '.' . $ext;

                Storage::disk('public')->put($filename, $response->body());

                // Update status sukses
                DB::table('voice_generations')->where('id', $generationId)->update([
                    'result_audio_path' => $filename,
                    'status' => 'completed',
                    'updated_at' => now(),
                ]);

                return response($response->body(), 200)
                    ->header('Content-Type', $enginePreference === 'elevenlabs' ? 'audio/mpeg' : 'audio/wav')
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

    /**
     * Get engine status
     */
    public function engineStatus()
    {
        $engines = [
            'xtts' => ['port' => 5000, 'name' => 'XTTS v2', 'quality' => 'Free / Good'],
            'gptsovits' => ['port' => 5001, 'name' => 'GPT-SoVITS', 'quality' => 'Indonesian Native'],
            'elevenlabs' => ['port' => 5002, 'name' => 'ElevenLabs', 'quality' => 'Premium']
        ];

        $results = [];
        foreach ($engines as $key => $info) {
            try {
                $status = Http::timeout(1)->get("http://localhost:{$info['port']}/health");
                $results[$key] = array_merge($info, [
                    'available' => $status->successful(),
                    'details' => $status->json()
                ]);
            } catch (\Exception $e) {
                $results[$key] = array_merge($info, ['available' => false]);
            }
        }

        return response()->json(['engines' => $results]);
    }
}
