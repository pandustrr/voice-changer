<?php

namespace App\Services;

use Illuminate\Support\Facades\Http;

class ModalService
{
    /**
     * Call Modal.com API for voice generation
     */
    public function generateVoice($text, $model_path, $speaker_ref)
    {
        $apiKey = config('services.modal.api_key');
        $generateUrl = env('AI_GENERATE_URL', 'http://127.0.0.1:5000/generate');

        if (!$apiKey) {
            // Local Fallback
            $response = Http::asForm()->post($generateUrl, [
                'text' => $text,
                'model_path' => $model_path,
                'speaker_ref' => $speaker_ref
            ]);

            return $response->body();
        }

        // $response = Http::withToken($apiKey)->post('https://your-modal-app.modal.run', [
        //     'text' => $text,
        //     'model' => $model_path,
        //     'speaker' => $speaker_ref
        // ]);

        return "audio_url_or_binary";
    }
}
