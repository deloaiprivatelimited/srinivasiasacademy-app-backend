import boto3
from dotenv import load_dotenv
import os
from PIL import Image
import io
from concurrent.futures import ThreadPoolExecutor, as_completed

load_dotenv()

def process_object(s3, bucket_name, key):
    print(f"Processing: {key}")

    # Download
    try:
        original = s3.get_object(Bucket=bucket_name, Key=key)["Body"].read()
        image = Image.open(io.BytesIO(original)).convert("RGB")
        original_size = len(original)
    except Exception as e:
        return f"❌ Failed {key}: {e}"

    # Optimize dimensions (max 2000px for web)
    max_width = 2000
    if image.width > max_width:
        ratio = max_width / image.width
        new_height = int(image.height * ratio)
        image = image.resize((max_width, new_height), Image.Resampling.LANCZOS)

    # Convert to WebP with optimal settings
    buffer = io.BytesIO()
    image.save(
        buffer, 
        "webp", 
        quality=80,
        method=6  # Slower but better compression
    )
    buffer.seek(0)
    optimized_size = len(buffer.getvalue())

    # New key
    new_key = key.rsplit(".", 1)[0] + ".webp"

    # Upload WebP
    s3.put_object(
        Bucket=bucket_name,
        Key=new_key,
        Body=buffer,
        ContentType="image/webp",
        CacheControl="public, max-age=31536000"  # 1 year cache
    )

    # Remove original
    s3.delete_object(Bucket=bucket_name, Key=key)

    reduction = ((original_size - optimized_size) / original_size) * 100
    return f"✅ Optimized: {key} → {new_key} | Size: {original_size/1024:.1f}KB → {optimized_size/1024:.1f}KB ({reduction:.1f}% reduction)"


def convert_to_webp(bucket_name, workers=8):
    s3 = boto3.client(
        "s3",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        region_name=os.getenv("AWS_REGION")
    )

    paginator = s3.get_paginator("list_objects_v2")

    keys = []
    for page in paginator.paginate(Bucket=bucket_name):
        for obj in page.get("Contents", []):
            key = obj["Key"]
            if key.lower().endswith((".jpg", ".jpeg", ".png")):
                keys.append(key)

    print(f"Found {len(keys)} image files")

    # Use 8 threads
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {executor.submit(process_object, s3, bucket_name, key): key for key in keys}

        for future in as_completed(futures):
            print(future.result())

    print("Done!")


if __name__ == "__main__":
    bucket = os.getenv("AWS_BUCKET")
    if not bucket:
        raise ValueError("AWS_BUCKET not set")

    convert_to_webp(bucket, workers=8)
