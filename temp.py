#!/usr/bin/env python3
"""
Optimize WebP images stored in S3 bucket. Can load AWS credentials from a .env file
or use the standard AWS credential provider chain (env, ~/.aws/credentials, IAM role).
Downloads objects to memory, re-encodes, and uploads back only when smaller.
"""

import argparse
import io
import os
import sys
from PIL import Image
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from dotenv import load_dotenv

def load_env_file(env_path):
    # Loads a .env file into the environment (does not print secrets)
    if env_path and os.path.exists(env_path):
        load_dotenv(env_path)
        print(f"Loaded environment variables from: {env_path}")
    elif env_path:
        print(f"Warning: .env file not found at {env_path}", file=sys.stderr)

def ensure_credentials_present():
    # Quick check to see if credentials are present via env vars.
    ak = os.environ.get("AWS_ACCESS_KEY_ID")
    sk = os.environ.get("AWS_SECRET_ACCESS_KEY")
    token = os.environ.get("AWS_SESSION_TOKEN")
    if ak and sk:
        print("AWS credentials found in environment (using these).")
        return True
    # Do not fail here — boto3 can still find credentials via other means (profile/role)
    return False

def optimize_bytes(data_bytes, quality=80, method=6):
    with Image.open(io.BytesIO(data_bytes)) as im:
        if im.mode not in ("RGB", "RGBA"):
            im = im.convert("RGB")
        out = io.BytesIO()
        im.save(out, format="WEBP", quality=quality, method=method, lossless=False)
        return out.getvalue()

def process_s3_bucket(bucket, prefix="", quality=80, method=6, dry_run=False,
                      region=None, backup_prefix=None, force_replace=False):
    # Use boto3 default session (reads env, config file, or role)
    session_kwargs = {}
    if region:
        session_kwargs['region_name'] = region
    s3 = boto3.client("s3", **session_kwargs)

    paginator = s3.get_paginator("list_objects_v2")
    kwargs = {"Bucket": bucket}
    if prefix:
        kwargs["Prefix"] = prefix

    total_saved = 0
    replaced = 0

    for page in paginator.paginate(**kwargs):
        for obj in page.get("Contents", []):
            key = obj["Key"]
            if not key.lower().endswith(".webp"):
                continue
            try:
                resp = s3.get_object(Bucket=bucket, Key=key)
                orig_body = resp["Body"].read()
                new_body = optimize_bytes(orig_body, quality=quality, method=method)

                should_replace = force_replace or (len(new_body) < len(orig_body))
                saved = len(orig_body) - len(new_body)

                if should_replace:
                    print(f"{key}: {len(orig_body)} -> {len(new_body)} (saved {saved} bytes) | replacing")
                    if not dry_run:
                        # Backup original to backup_prefix if requested
                        if backup_prefix:
                            # Construct backup key: backup_prefix + original key path
                            backup_key = backup_prefix.rstrip("/") + "/" + key
                            try:
                                s3.copy_object(
                                    Bucket=bucket,
                                    CopySource={'Bucket': bucket, 'Key': key},
                                    Key=backup_key
                                )
                                print(f"  backed up original to: {backup_key}")
                            except Exception as e:
                                print(f"  warning: failed to backup {key} -> {backup_key}: {e}", file=sys.stderr)
                        # Preserve existing ContentType if present
                        content_type = resp.get("ContentType", "image/webp")
                        s3.put_object(Bucket=bucket, Key=key, Body=new_body, ContentType=content_type)
                    total_saved += max(0, saved)
                    replaced += 1
                else:
                    print(f"{key}: no improvement ({len(orig_body)} -> {len(new_body)}) | skipped")
            except ClientError as e:
                print(f"Failed {key}: {e}", file=sys.stderr)
            except Exception as e:
                print(f"Error processing {key}: {e}", file=sys.stderr)

    print(f"\nSummary: replaced {replaced} objects, total saved {total_saved} bytes")

def main():
    p = argparse.ArgumentParser(description="Optimize WebP images in an S3 bucket (optionally load .env)")
    p.add_argument("--bucket", required=True, help="S3 bucket name")
    p.add_argument("--prefix", default="", help="Prefix to limit objects")
    p.add_argument("--quality", type=int, default=80, help="Quality 0-100")
    p.add_argument("--method", type=int, default=6, help="Method 0-6")
    p.add_argument("--dry-run", action="store_true", help="Don't upload changes")
    p.add_argument("--region", default=None, help="AWS region (optional)")
    p.add_argument("--env-file", default=None, help="Path to .env file to load AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY")
    p.add_argument("--backup-prefix", default=None, help="S3 prefix to store backups (e.g. backups/). If omitted, no backup copy is made.")
    p.add_argument("--force", action="store_true", help="Force replace even if not smaller")
    args = p.parse_args()

    # Load .env first if provided
    if args.env_file:
        load_env_file(args.env_file)

    creds_in_env = ensure_credentials_present()
    if not creds_in_env:
        print("Note: AWS credentials NOT found in environment variables. boto3 will attempt other credential sources (config file, profile, or IAM role).", file=sys.stderr)

    try:
        # Quick credentials test (optional)
        sts = boto3.client("sts", region_name=args.region) if args.region else boto3.client("sts")
        try:
            caller = sts.get_caller_identity()
            print(f"Using AWS account: {caller.get('Account')} principal: {caller.get('Arn')}")
        except NoCredentialsError:
            print("No AWS credentials available to validate via STS. Proceeding but calls may fail.", file=sys.stderr)
        except Exception as e:
            print(f"Warning: could not validate credentials via STS: {e}", file=sys.stderr)
    except Exception:
        pass

    process_s3_bucket(
        args.bucket,
        prefix=args.prefix,
        quality=args.quality,
        method=args.method,
        dry_run=args.dry_run,
        region=args.region,
        backup_prefix=args.backup_prefix,
        force_replace=args.force
    )

if __name__ == "__main__":
    main()
