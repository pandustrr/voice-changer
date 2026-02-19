import boto3
import os

class S3Manager:
    def __init__(self):
        # Modal secrets akan mensuplai env variables ini
        self.s3 = boto3.client(
            's3',
            endpoint_url=os.environ.get('AWS_ENDPOINT'),
            aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
            region_name=os.environ.get('AWS_DEFAULT_REGION', 'auto')
        )
        self.bucket = os.environ.get('AWS_BUCKET')

    def download_model_if_not_exists(self, remote_path, local_dir):
        """Ambil model dari S3 ke cache Modal jika belum ada"""
        if not os.path.exists(local_dir):
            os.makedirs(local_dir, exist_ok=True)
            
        print(f"🔍 Checking model in S3: {remote_path}")
        objects = self.s3.list_objects_v2(Bucket=self.bucket, Prefix=remote_path)
        
        if 'Contents' in objects:
            for obj in objects['Contents']:
                file_key = obj['Key']
                filename = os.path.basename(file_key)
                local_file = os.path.join(local_dir, filename)
                
                if not os.path.exists(local_file):
                    print(f"📥 Downloading {filename}...")
                    self.s3.download_file(self.bucket, file_key, local_file)
        
        return local_dir
