from dotenv import load_dotenv
import boto3
import os
from models.course import Course,CourseCounters
from mongoengine import connect
from models.student import Student
from models.chapter import Chapter, TextChapter,AudioChapter,VideoChapter,LiveClass,PDFChapter
from urllib.parse import quote

# Load .env environment variables
load_dotenv()

# Read environment variables
aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
aws_region = os.getenv("AWS_REGION")
bucket_name = os.getenv("AWS_BUCKET")
connect(host=os.getenv("MONGO_URI"))

COURSE_DB_ID = "691dcd778997f0596bf231f3"  # _id of the course document in Mongo
S3_BASE_URL = "https://srinivas-ias-academy.s3.amazonaws.com/"
COMMON_THUMBNAIL = "https://d1ytcm2rfo0yep.cloudfront.net/files/thumbnails/srinivas_ias_Academy_logo.jpeg"

# Create S3 client
s3 = boto3.client(
    "s3",
    region_name=aws_region,
    aws_access_key_id=aws_access_key,
    aws_secret_access_key=aws_secret_key
)


# List object keys in bucket
response = s3.list_objects_v2(Bucket=bucket_name)

ALL_S3_KEYS = []

if "Contents" in response:
    for obj in response["Contents"]:
        ALL_S3_KEYS.append(obj["Key"])
else:
    print("No objects found")

print(ALL_S3_KEYS)

def get_video_duration_from_url(url: str) -> str:
    """
    Returns duration as a string like 'HH:MM:SS' or 'MM:SS'.
    If anything fails, returns empty string.
    """
    try:
        from moviepy.editor import VideoFileClip
        clip = VideoFileClip(url)
        total_seconds = int(clip.duration)
        clip.close()

        minutes, seconds = divmod(total_seconds, 60)
        hours, minutes = divmod(minutes, 60)

        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes:02d}:{seconds:02d}"
    except Exception as e:
        print(f"Could not get duration for {url}: {e}")
        return ""

def is_karnataka_history_video(key: str) -> bool:
    key = key.strip()
    print(key)

    allowed_prefixes = [
        "HISTORY/Moderv_History_videos/"
    ]

    upper_key = key
    print(upper_key)

    # Must start with one of the allowed folders
    if not any(upper_key.startswith(prefix) for prefix in allowed_prefixes):
        return False

    # Ignore folders
    if key.endswith("/"):
        return False

    # Allow only video extensions
    return key.lower().endswith((".mp4", ".m4v", ".mov", ".avi", ".mkv"))

def key_to_title(key: str) -> str:
    filename = os.path.basename(key)
    name, _ = os.path.splitext(filename)
    # Normalise extra whitespace, optional: underscores to spaces
    name = name.replace("_", " ")
    return " ".join(name.split())

def key_to_s3_url(key: str) -> str:
    # URL-encode spaces and unicode correctly, but keep slashes
    encoded_key = quote(key, safe="/")
    return S3_BASE_URL + encoded_key


print("Courses in database:")
for course in Course.objects:
    print(f"{course.id} - {course.name}")


course = Course.objects(id=COURSE_DB_ID).first()
if not course:
    raise ValueError(f"Course with _id={COURSE_DB_ID} not found")

for key in ALL_S3_KEYS:
    key = key.strip()

    if not is_karnataka_history_video(key):
        print(f"Skipping key: {key}")
        continue
    else:
        print(f"Processing key: {key}")

    title = key_to_title(key)
    print(title)


    raw_url = key_to_s3_url(key)
    video_url = raw_url
    print(video_url)
    # exit()

    # duration = get_video_duration_from_url(video_url)

    video_chapter = VideoChapter(
        video_url=video_url,
        thumbnail=COMMON_THUMBNAIL,
        title=title,
        duration= ""  
    )

    chapter = Chapter(
        type="video",
        video=video_chapter,
        demo=False
    )
    chapter.save()

    course.chapters.append(chapter)
    

    print(f"Created chapter: {title} | URL: {video_url} ")

course.save()
# print("All Karnataka History video chapters added to the course.")
