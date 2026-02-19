<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class VoiceModel extends Model
{
    protected $fillable = ['user_id', 'name', 's3_path', 'status'];
}
