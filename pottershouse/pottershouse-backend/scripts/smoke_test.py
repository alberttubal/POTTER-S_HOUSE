# scripts/smoke_test.py
import os
import sys
import time
import psycopg2
import redis
import boto3
import django

print("python:", sys.version.splitlines()[0])
print("django:", django.get_version())

# PostgreSQL connection info
PG_USER = os.getenv("POSTGRES_USER", "potter")
PG_PASSWORD = os.getenv("POSTGRES_PASSWORD", "potterpass")
PG_DB = os.getenv("POSTGRES_DB", "potter_dev")
PG_HOST = os.getenv("POSTGRES_HOST", "localhost")
PG_PORT = int(os.getenv("POSTGRES_PORT", 5432))

# Postgres - retry until ready
for attempt in range(10):
    try:
        conn = psycopg2.connect(
            dbname="potter_dev",
            user="potter",
            password="potterpass",
            host="localhost",
            port=5433,
        )
        cur = conn.cursor()
        cur.execute("SELECT now()")
        print("Postgres ok:", cur.fetchone())
        cur.close()
        conn.close()
        break
    except Exception as e:
        print(f"Postgres not ready, retrying ({attempt+1}/10):", e)
        time.sleep(3)
else:
    print("Postgres connection failed after 10 attempts")

# Redis
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
try:
    r = redis.Redis.from_url(REDIS_URL)
    print("Redis ok:", r.ping())
except Exception as e:
    print("Redis error:", e)

# MinIO / S3
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "http://127.0.0.1:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minioadmin")
try:
    s3 = boto3.client(
        "s3",
        endpoint_url=MINIO_ENDPOINT,
        aws_access_key_id=MINIO_ACCESS_KEY,
        aws_secret_access_key=MINIO_SECRET_KEY,
    )
    print("MinIO buckets:", s3.list_buckets().get("Buckets"))
except Exception as e:
    print("MinIO not ready or credentials incorrect:", e)
