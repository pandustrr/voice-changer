<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class CharacterVoice extends Model
{
    protected $fillable = ['name', 'description', 'thumbnail', 'is_premium'];
}
