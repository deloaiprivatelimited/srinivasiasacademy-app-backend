# s3_presign/routes.py
from flask import Blueprint, request, jsonify
import boto3
import os

s3_presign_bp = Blueprint("s3_presign_bp",__name__, url_prefix="/api/s3")

s3_client = boto3.client(
    "s3",
    region_name=os.getenv("AWS_REGION"),
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
)

BUCKET_NAME = os.getenv("BUCKET_NAME")
S3_BASE_URL = f"https://{BUCKET_NAME}.s3.amazonaws.com"

@s3_presign_bp.route("/presign", methods=["POST"])
def generate_presigned_url():
    """
    POST /api/s3/presign
    Body JSON: { "fileName": "name.png", "fileType": "image/png", "path": "uploads/user1" }
    Response: { "uploadUrl": "...", "key": "uploads/user1/name.png", "fileUrl": "https://.../uploads/..." }
    """
    data = request.get_json() or {}
    file_name = data.get("fileName")
    content_type = data.get("fileType", "application/octet-stream")
    path = data.get("path", "")

    if not file_name:
        return jsonify({"error": "Missing 'fileName' in body"}), 400

    # Sanitize path/key as needed (example: strip leading slashes)
    key = f"{path.rstrip('/')}/{file_name}".lstrip('/')

    try:
        upload_url = s3_client.generate_presigned_url(
            ClientMethod="put_object",
            Params={
                "Bucket": BUCKET_NAME,
                "Key": key,
                # "ContentType": content_type
            },
            ExpiresIn=300
        )

        return jsonify({
            "uploadUrl": upload_url,
            "key": key,
            "fileUrl": f"{S3_BASE_URL}/{key}",
            "expiresIn": 300
        })
    except Exception as e:
        print("Error generating presigned URL:", e)
        return jsonify({"error": "Failed to generate presigned URL"}), 500
