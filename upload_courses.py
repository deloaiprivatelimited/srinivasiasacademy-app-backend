import csv
from urllib.parse import quote
from mongoengine import connect
from models.chapter import Chapter  # Import the Chapter model from your MongoDB models
from models.course import Course  # Import the Course model

# MongoDB Connection
connect(db="test", host="localhost", port=27017)

# Input parameters
course_id = "COURSE0016"
thumnail_url = "https://azadicsacademy.s3.ap-southeast-2.amazonaws.com/files/thumbnails/Computer-64e784a0-ec9b-4d4a-922e-e5acac88b25a/Screenshot%202025-01-09%20at%2011.29.30%E2%80%AFAM.png"
video_url_prefix = "https://azadicsacademy.s3.ap-southeast-2.amazonaws.com/"

# Function to convert filenames to title case
def convert_to_title(filename):
    title = filename.replace(".mp4", "").replace("_", " ").title()
    return title

# Find the course by course_id
course = Course.objects(course_id=course_id).first()
if not course:
    raise ValueError(f"Course with ID {course_id} not found")

# Read the input CSV and create chapters
csv_file_path = "input.csv"
with open(csv_file_path, "r") as csv_file:
    reader = csv.reader(csv_file)

    for row in reader:
        _, category, part, filename, key = row

        # Generate chapter details
        chapter_title = convert_to_title(filename)
        video_url = video_url_prefix + quote(key)

        # Create chapter payload
        chapter_payload = {
            "type": "video",
            "video": {
                "video_url": video_url,
                "thumbnail": thumnail_url,
                "title": chapter_title,
                "duration": "5",  # Fixed duration as string
                "professor": "SRINIVASA SIR",
                "notes": ""
            },
            "demo": False  # Adjust if you want the chapter to be a preview
        }

        # Save chapter to the database
        chapter = Chapter(**chapter_payload)
        chapter.save()

        # Add the chapter to the course
        course.chapters.append(chapter)

        # Print confirmation
        print(f"Chapter '{chapter_title}' added to course '{course_id}' with ID: {chapter.id}")

# Save the updated course
course.save()

print("All chapters have been processed and added to the course.")
