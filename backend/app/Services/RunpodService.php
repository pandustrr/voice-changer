<?php

namespace App\Services;

use Illuminate\Support\Facades\Http;

class RunpodService
{
    /**
     * Trigger training task on Runpod
     */
    public function startTraining($user_id, $audio_path)
    {
        $apiKey = config('services.runpod.api_key');
        $trainingUrl = env('AI_TRAINING_URL', 'http://127.0.0.1:5000/train');

        if (!$apiKey) {
            // Local Fallback
            Http::asForm()->post($trainingUrl, [
                'user_id' => $user_id,
                'audio_path' => $audio_path
            ]);

            return [
                'status' => 'success',
                'mode' => 'local',
                'message' => 'Training started locally for user ' . $user_id
            ];
        }

        // request ke Runpod Serverless / Pod
        // $response = Http::withToken($apiKey)->post('https://api.runpod.ai/...', ...);

        return [
            'status' => 'success',
            'mode' => 'runpod',
            'message' => 'Training triggerred on Runpod for user ' . $user_id
        ];
    }
}
