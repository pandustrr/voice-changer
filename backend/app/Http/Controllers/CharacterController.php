<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use App\Models\CharacterVoice;

class CharacterController extends Controller
{
    public function index()
    {
        return CharacterVoice::all();
    }

    public function show($id)
    {
        return CharacterVoice::findOrFail($id);
    }
}
