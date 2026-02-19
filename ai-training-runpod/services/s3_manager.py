import boto3
import os
from dotenv import load_dotenv

load_dotenv()

class S3Manager:
    def __init__(self):
        self.s3 = boto3.client(
            's3',
            endpoint_url=os.getenv('AWS_ENDPOINT'),
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('AWS_DEFAULT_REGION', 'auto')
        )
        self.bucket = os.getenv('AWS_BUCKET')

    def download_folder(self, remote_path, local_path):
        """Download dataset dari S3 ke worker Runpod"""
        print(f"📥 Downloading dataset from {remote_path}...")
        os.makedirs(local_path, exist_ok=True)
        
        paginator = self.s3.get_paginator('list_objects_v2')
        for result in paginator.paginate(Bucket=self.bucket, Prefix=remote_path):
            if 'Contents' in result:
                for obj in result['Contents']:
                    key = obj['Key']
                    if not key.endswith('/'):
                        filename = os.path.basename(key)
                        self.s3.download_file(self.bucket, key, os.path.join(local_path, filename))

    def upload_model(self, local_model_dir, remote_model_path):
        """Upload hasil training (.pth, config.json) ke Cloud"""
        print(f"📤 Uploading model to {remote_model_path}...")
        for root, dirs, files in os.walk(local_model_dir):
            for file in files:
                if file.endswith(('.pth', '.json', '.txt')):
                    local_file = os.path.join(root, file)
                    remote_file = os.path.join(remote_model_path, file)
                    self.s3.upload_file(local_file, self.bucket, remote_file)
        print("✅ Model uploaded successfully!")
