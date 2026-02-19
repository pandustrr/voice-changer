<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up()
    {
        Schema::create('character_voices', function (Blueprint $table) {
            $table->id();
            $table->string('name');
            $table->text('description')->nullable();
            $table->string('thumbnail')->nullable();
            $table->string('model_ref_path');
            $table->boolean('is_premium')->default(false);
            $table->timestamps();
        });
    }

    public function down()
    {
        Schema::dropIfExists('character_voices');
    }
};
