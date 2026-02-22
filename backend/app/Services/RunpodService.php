<?php

namespace App\Services;

use Illuminate\Support\Facades\Http;

class RunpodService
{
    public function train(array $params)
    {
        $apiKey = env('RUNPOD_API_KEY');
        $trainingUrl = env('AI_TRAINING_URL');

        // Jika URL menggunakan Proxy RunPod, kirim data LANGSUNG (Direct)
        // Jika URL menggunakan API Runpod Serverless (v1/xxx/run), baru pakai 'input'
        $isProxy = str_contains($trainingUrl, 'proxy.runpod.net');

        if ($isProxy) {
            $response = Http::withHeaders([
                'Authorization' => "Bearer $apiKey",
                'Content-Type' => 'application/json',
            ])->post($trainingUrl, $params); // Tanpa pembungkus 'input'
        } else {
            $response = Http::withHeaders([
                'Authorization' => "Bearer $apiKey",
                'Content-Type' => 'application/json',
            ])->post($trainingUrl, [
                'input' => $params // Khusus Serverless API
            ]);
        }

        return $response->json();
    }
}
