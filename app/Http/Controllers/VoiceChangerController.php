<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\Storage;

class VoiceChangerController extends Controller
{
    public function clone(Request $request)
    {
        $request->validate([
            'audio' => 'required|file',
            'text' => 'required|string',
        ]);

        $audio = $request->file('audio');
        $text = $request->input('text');

        // Send to Python Backend
        try {
            // We use attach to send the file
            $response = Http::attach(
                'audio',
                file_get_contents($audio->getRealPath()),
                $audio->getClientOriginalName()
            )->post('http://localhost:5000/clone', [
                'text' => $text,
            ]);

            if ($response->successful()) {
                return response($response->body(), 200)
                    ->header('Content-Type', 'audio/wav');
            }

            return response()->json(['error' => 'Python backend error: ' . $response->body()], 500);
        } catch (\Exception $e) {
            return response()->json(['error' => 'Could not connect to Python backend. Is it running?'], 500);
        }
    }
}
