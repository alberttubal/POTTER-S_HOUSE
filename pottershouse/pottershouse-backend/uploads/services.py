import json
import os
from functools import lru_cache

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError

ALLOWED_MIME = {"image/jpeg", "image/png", "image/webp"}
MAX_SIZE = 5 * 1024 * 1024


def get_bucket_name():
    bucket = os.getenv("AWS_STORAGE_BUCKET_NAME", "").strip()
    if not bucket:
        raise RuntimeError("AWS_STORAGE_BUCKET_NAME is not configured")
    return bucket


def get_s3_client():
    return boto3.client(
        "s3",
        endpoint_url=os.getenv("AWS_S3_ENDPOINT_URL") or None,
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        region_name=os.getenv("AWS_S3_REGION_NAME"),
        config=Config(signature_version="s3v4"),
    )


def _public_read_enabled():
    return os.getenv("S3_PUBLIC_READ_ENABLED", "True").lower() == "true"


def _public_read_policy(bucket):
    return json.dumps(
        {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "PublicReadGetObject",
                    "Effect": "Allow",
                    "Principal": "*",
                    "Action": ["s3:GetObject"],
                    "Resource": [f"arn:aws:s3:::{bucket}/*"],
                }
            ],
        }
    )


def _ensure_public_read_policy(s3, bucket):
    if not _public_read_enabled():
        return
    s3.put_bucket_policy(Bucket=bucket, Policy=_public_read_policy(bucket))


@lru_cache(maxsize=1)
def ensure_bucket_exists():
    s3 = get_s3_client()
    bucket = get_bucket_name()

    bucket_exists = True
    try:
        s3.head_bucket(Bucket=bucket)
    except ClientError as exc:
        code = str(exc.response.get("Error", {}).get("Code", ""))
        if code not in {"404", "NoSuchBucket", "NotFound"}:
            raise
        bucket_exists = False

    if not bucket_exists:
        region = (os.getenv("AWS_S3_REGION_NAME") or "us-east-1").strip()
        create_kwargs = {"Bucket": bucket}
        if region and region != "us-east-1":
            create_kwargs["CreateBucketConfiguration"] = {"LocationConstraint": region}

        try:
            s3.create_bucket(**create_kwargs)
        except ClientError as exc:
            code = str(exc.response.get("Error", {}).get("Code", ""))
            if code not in {"BucketAlreadyOwnedByYou", "BucketAlreadyExists"}:
                raise

    _ensure_public_read_policy(s3, bucket)
    return bucket


def build_public_url(key):
    cdn = os.getenv("AWS_S3_CUSTOM_DOMAIN")
    bucket = get_bucket_name()

    if cdn:
        base = cdn if cdn.startswith("http") else f"https://{cdn}"
        return f"{base.rstrip('/')}/{key}"

    public_endpoint = os.getenv("AWS_S3_PUBLIC_ENDPOINT") or os.getenv("AWS_S3_ENDPOINT_URL")
    if public_endpoint:
        return f"{public_endpoint.rstrip('/')}/{bucket}/{key}"

    return f"https://{bucket}.s3.amazonaws.com/{key}"


def validate_upload(mime_type, size):
    if mime_type not in ALLOWED_MIME:
        raise ValueError("invalid_mime_type")
    if size > MAX_SIZE:
        raise ValueError("file_too_large")


def upload_fileobj(file_obj, key, mime_type):
    s3 = get_s3_client()
    bucket = ensure_bucket_exists()
    extra = {"ContentType": mime_type}
    acl = os.getenv("AWS_DEFAULT_ACL")
    if acl:
        extra["ACL"] = acl
    s3.upload_fileobj(file_obj, bucket, key, ExtraArgs=extra)


def generate_presigned_url(key, mime_type):
    s3 = get_s3_client()
    bucket = ensure_bucket_exists()
    return s3.generate_presigned_url(
        "put_object",
        Params={"Bucket": bucket, "Key": key, "ContentType": mime_type},
        ExpiresIn=3600,
    )
