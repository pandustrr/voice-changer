<?php

namespace App\Services;

use Illuminate\Support\Facades\Storage;

class StorageService
{
    /**
     * Handle S3 / Cloud Storage logic
     */
    public function uploadToCloud($localPath, $cloudPath)
    {
        $disk = config('filesystems.disks.s3.key') ? 's3' : 'public';
        return Storage::disk($disk)->put($cloudPath, file_get_contents($localPath));
    }

    public function getPresignedUrl($path)
    {
        $disk = config('filesystems.disks.s3.key') ? 's3' : 'public';

        /** @var \Illuminate\Filesystem\FilesystemAdapter $diskObj */
        $diskObj = Storage::disk($disk);

        return $diskObj->url($path);
    }
}
