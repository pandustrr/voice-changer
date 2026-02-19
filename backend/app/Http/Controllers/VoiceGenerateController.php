<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use App\Services\ModalService;

class VoiceGenerateController extends Controller
{
    protected $modal;

    public function __construct(ModalService $modal)
    {
        $this->modal = $modal;
    }

    public function generate(Request $request)
    {
        $request->validate(['text' => 'required', 'voice_id' => 'required']);

        // Call Modal for fast inference
        $audio = $this->modal->generateVoice($request->text, $request->voice_id, $request->speaker_ref);

        return response($audio)->header('Content-Type', 'audio/wav');
    }
}
