<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use App\Services\RunpodService;

class VoiceTrainingController extends Controller
{
    protected $runpod;

    public function __construct(RunpodService $runpod)
    {
        $this->runpod = $runpod;
    }

    public function store(Request $request)
    {
        $request->validate(['audio' => 'required|file']);

        // 1. Upload ke S3
        // 2. Trigger Runpod
        $userId = $request->user()?->id;
        $this->runpod->startTraining($userId, $request->file('audio')->path());

        return response()->json(['message' => 'Training started']);
    }
}
