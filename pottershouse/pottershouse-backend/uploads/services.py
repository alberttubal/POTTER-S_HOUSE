import os 
import uuid 
import boto3 
from botocore.config import Config 
 
ALLOWED_MIME = {'image/jpeg', 'image/png', 'image/webp'} 
MAX_SIZE = 5 * 1024 * 1024 
 
def get_s3_client(): 
    return boto3.client( 
        's3', 
        endpoint_url=os.getenv('AWS_S3_ENDPOINT_URL') or None, 
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'), 
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'), 
        region_name=os.getenv('AWS_S3_REGION_NAME'), 
        config=Config(signature_version='s3v4'), 
    ) 
 
def build_public_url(key): 
    cdn = os.getenv('AWS_S3_CUSTOM_DOMAIN') 
    endpoint = os.getenv('AWS_S3_ENDPOINT_URL') 
    bucket = os.getenv('AWS_STORAGE_BUCKET_NAME') 
    if cdn: 
        base = cdn if cdn.startswith('http') else f'https://{cdn}' 
        return f'{base}/{key}' 
    if endpoint: 
        endpoint = endpoint.rstrip('/') 
        return f'{endpoint}/{bucket}/{key}' 
    return f'https://{bucket}.s3.amazonaws.com/{key}' 
 
def validate_upload(mime_type, size): 
    if mime_type not in ALLOWED_MIME: 
        raise ValueError('invalid_mime_type') 
    if size > MAX_SIZE: 
        raise ValueError('file_too_large') 
 
def upload_fileobj(file_obj, key, mime_type):
    s3 = get_s3_client()
    bucket = os.getenv('AWS_STORAGE_BUCKET_NAME')
    extra = {'ContentType': mime_type}
    acl = os.getenv('AWS_DEFAULT_ACL')
    if acl:
        extra['ACL'] = acl
    s3.upload_fileobj(file_obj, bucket, key, ExtraArgs=extra)


def generate_presigned_url(key, mime_type): 
    s3 = get_s3_client() 
    bucket = os.getenv('AWS_STORAGE_BUCKET_NAME') 
    return s3.generate_presigned_url( 
        'put_object', 
        Params={'Bucket': bucket, 'Key': key, 'ContentType': mime_type}, 
        ExpiresIn=3600, 
    )
