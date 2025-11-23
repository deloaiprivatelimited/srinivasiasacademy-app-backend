import os
from urllib.parse import quote

from mongoengine import (
    connect, Document, EmbeddedDocument,
    StringField, ListField, ReferenceField, DecimalField,
    IntField, EmbeddedDocumentField, BooleanField
)
from mongoengine.fields import URLField

# -------------------- DB CONNECTION --------------------
# Adjust these to your environment:
connect(
    db="YOUR_DB_NAME",
    host="mongodb://localhost:27017/YOUR_DB_NAME"  # or your Atlas / other URI
)

# -------------------- MODELS (if not already imported) --------------------
# If you already have these in models/, just import them instead of redefining.

class CourseCounters(Document):
    max_course_id = IntField(default=0)

class PDFChapter(EmbeddedDocument):
    title = StringField(required=True)
    pdf_url = URLField(required=True)

class AudioChapter(EmbeddedDocument):
    title = StringField(required=True)
    audio_url = URLField(required=True)

class TextChapter(EmbeddedDocument):
    title = StringField(required=True)
    text = StringField(required=True)

class VideoChapter(EmbeddedDocument):
    video_url = URLField(required=True)
    thumbnail = URLField(required=False, default='')
    title = StringField(required=True)
    duration = StringField(required=True, default='')
    professor = StringField(required=False, default=' ')
    notes = StringField(default='')

class LiveClass(EmbeddedDocument):
    title = StringField(required=True)
    start_date = StringField(required=True)
    start_time = StringField(required=True)
    duration = StringField(required=True)
    link = StringField(default='')

class Chapter(Document):
    meta = {'collection': 'chapters'}

    type = StringField(required=True, choices=['pdf', 'text', 'video', 'live_class', 'audio'])
    pdf = EmbeddedDocumentField(PDFChapter)
    audio = EmbeddedDocumentField(AudioChapter)
    text = EmbeddedDocumentField(TextChapter)
    video = EmbeddedDocumentField(VideoChapter)
    demo = BooleanField(default=False)
    live_class = EmbeddedDocumentField(LiveClass)

class Course(Document):
    meta = {'collection': 'courses'}

    name = StringField(required=True)
    topics = ListField(StringField())
    professors = ListField(StringField())
    price = DecimalField(precision=2, required=True)
    whole_duration = StringField(default="0")
    chapters = ListField(ReferenceField(Chapter))
    thumbnail_url = StringField()
    course_id = StringField(unique=True)
    students_enrolled = ListField(ReferenceField('Student'))

# If you already have replace_with_cloudfront in models.chapter, import that instead:
try:
    from models.chapter import replace_with_cloudfront
except ImportError:
    # Fallback stub if not imported; replace with your real logic
    def replace_with_cloudfront(url: str) -> str:
        # e.g. replace S3 domain with CloudFront distribution
        # return url.replace("https://srinivas-ias-academy.s3.amazonaws.com", "https://your-cloudfront-domain")
        return url

# -------------------- CONFIG --------------------
COURSE_DB_ID = "691dcd778997f0596bf231f3"  # _id of the course document in Mongo
S3_BASE_URL = "https://srinivas-ias-academy.s3.amazonaws.com/"
COMMON_THUMBNAIL = "https://srinivas-ias-academy.s3.amazonaws.com/gallery-images/WhatsApp_Image_2025-11-17_at_11.25.52_PM.jpeg"

# All S3 keys you listed (you can also read this from a file or AWS SDK)
ALL_S3_KEYS = [
    "History/Anciant_History/pallavas of kanchi/Pallavas Of Kanchi ,( ಕಂಚಿಯ ಪಲ್ಲವರು )..m4v",
    "History/Anciant_History/ಕ್ರಿ,ಪೂ  6ನೇ ಶತಮಾನದ ಧಾರ್ಮಿಕ ಸುಧಾರಣಾ ಚಳುವಳಿಗಳು/Age Of Philosophy.m4v",
    "History/Anciant_History/ಕ್ರಿ,ಪೂ  6ನೇ ಶತಮಾನದ ಧಾರ್ಮಿಕ ಸುಧಾರಣಾ ಚಳುವಳಿಗಳು/Buddhism -  Buddhist Philosophy-(ಬೌದ್ಧ ಧರ್ಮದ ತತ್ವ )  And Buddhist Sang\nha-( ಬೌದ್ಧ ಸಂಘ  ) - Part - 2.m4v",
    "History/Anciant_History/ಕ್ರಿ,ಪೂ  6ನೇ ಶತಮಾನದ ಧಾರ್ಮಿಕ ಸುಧಾರಣಾ ಚಳುವಳಿಗಳು/Buddhist Council's, ( ಬೌದ್ಧ ಸಮ್ಮೇಳನಗಳು.) Part 3.mp4",
    "History/Anciant_History/ಕ್ರಿ,ಪೂ  6ನೇ ಶತಮಾನದ ಧಾರ್ಮಿಕ ಸುಧಾರಣಾ ಚಳುವಳಿಗಳು/Buddhist Literature, ( ಬೌದ್ಧ ಸಾಹಿತ್ಯ. ).mp4",
    "History/Anciant_History/ಕ್ರಿ,ಪೂ  6ನೇ ಶತಮಾನದ ಧಾರ್ಮಿಕ ಸುಧಾರಣಾ ಚಳುವಳಿಗಳು/Jainism  ( ಜೈನಧರ್ಮ )  Mahaveera & Jaina Philosophy  ( ಮಹಾವೀರ ಮತ್ತು ಜೈನ\nಧರ್ಮದ ತತ್ವ  ) Part - 1.m4v",
    "History/Anciant_History/ಕ್ರಿ,ಪೂ  6ನೇ ಶತಮಾನದ ಧಾರ್ಮಿಕ ಸುಧಾರಣಾ ಚಳುವಳಿಗಳು/Jainism ( ಜೈನಧರ್ಮ )  Jaina sangha & Jaina councils ( ಜೈನ ಸಂಘ ಮತ್ತು ಜೈನ\n ಸಮ್ಮೆಳನಗಳು ) Part - 2.mp4",
    "History/Anciant_History/ಕ್ರಿ,ಪೂ  6ನೇ ಶತಮಾನದ ಧಾರ್ಮಿಕ ಸುಧಾರಣಾ ಚಳುವಳಿಗಳು/Jainism ( ಜೈನಧರ್ಮ ) Spread of Jainism, Dicline of Jainism & Jaina Lite\nrature   ( ಜೈನಧರ್ಮದ ಏಳಿಗೆ, ಅವನತಿ ಮತ್ತು ಜೈನಸಾಹಿತ್ಯ ) Part - 3.m4v",
    "History/Anciant_History/ಕ್ರಿ,ಪೂ  6ನೇ ಶತಮಾನದ ಧಾರ್ಮಿಕ ಸುಧಾರಣಾ ಚಳುವಳಿಗಳು/Religioas Reform Movements in 6th Century BC  (ಕ್ರಿ,ಪೂ  6ನೇ ಶತಮಾನದ ಧಾರ\n್ಮಿಕ ಸುಧಾರಣಾ ಚಳುವಳಿಗಳು.).m4v",
    "History/Anciant_History/ಕ್ರಿ,ಪೂ  6ನೇ ಶತಮಾನದ ಧಾರ್ಮಿಕ ಸುಧಾರಣಾ ಚಳುವಳಿಗಳು/Spread of Buddhism ( ಬೌದ್ಧ ಧರ್ಮದ ಏಳಿಗೆ ) Part - 2.m4v",
    "History/Anciant_History/ಕ್ರಿ,ಪೂ  6ನೇ ಶತಮಾನದ ಧಾರ್ಮಿಕ ಸುಧಾರಣಾ ಚಳುವಳಿಗಳು/Spread of Buddhism ( ಬೌದ್ಧ ಧರ್ಮದ ಏಳಿಗೆ ).mp4",
    "History/Karnataka History/",
    "History/Karnataka History/3 Krw (1799 - 1831).mp4",
    "History/Karnataka History/Adil Shahis Of Bijapur (1489 - 1686).mp4",
    "History/Karnataka History/Administration  Of Vijaganagara.mp4",
    "History/Karnataka History/Ahmed Shah Wali Bahamani.mp4",
    "History/Karnataka History/Armed Rebellion In Karnataka.mp4",
    "History/Karnataka History/Bahamani Dynastis 1.mp4",
    "History/Karnataka History/Bahamani dynastis 2.mp4",
    "History/Karnataka History/Civil Disobedience Movement In Ka.mp4",
    "History/Karnataka History/Culteral Contributions Bc.mp4",
    "History/Karnataka History/Culteral Contributions Kc.mp4",
    "History/Karnataka History/Culteral contributions Bahamani.mp4",
    "History/Karnataka History/Cultural Contibutions Of Badami Chalukyas.mp4",
    "History/Karnataka History/Cultural Contributions Of Gangas.mp4",
    "History/Karnataka History/Cultural Contributions Of Kadambas-1.mp4",
    "History/Karnataka History/Cultural Contributions Of Rastrakutes.mp4",
    "History/Karnataka History/Cultural Contributions Of Vijayanagara.mp4",
    "History/Karnataka History/Cultural History Of Hoysales.mp4",
    "History/Karnataka History/Diwan Mirza Ismail (1926 - 1941).mp4",
    "History/Karnataka History/Diwan Rule Of Mysore ( 1881 - 1947 ).mp4",
    "History/Karnataka History/Freedom Movement In Karnataka (1885 -1947).mp4",
    "History/Karnataka History/Freedom movement in hyderabad karnataka.mp4",
    "History/Karnataka History/Gangas Of Talakadu (350 - 1004 Ad).mp4",
    "History/Karnataka History/Hoysalas of Dwarasamudra (1006 - 1346).mp4",
    "History/Karnataka History/Hyderali (1761 - 1782).mp4",
    "History/Karnataka History/Kadambas Of Banavasi.mp4",
    "History/Karnataka History/Kalyani Chalukyas.mp4",
    "History/Karnataka History/Mysore Wodeyars (1399 - 1947).mp4",
    "History/Karnataka History/Political History Of Badami Chalukyas 2.mp4",
    "History/Karnataka History/Political History Of Bc 3.mp4",
    "History/Karnataka History/Political History Of Gangas (350 - 1004Ad).mp4",
    "History/Karnataka History/Political History Of Hoysalas 1.mp4",
    "History/Karnataka History/Political History Of Hoysalas 2.mp4",
    "History/Karnataka History/Political History Of Kc.mp4",
    "History/Karnataka History/Political History R ( 750 Ad - 982 Ad) 1.mp4",
    "History/Karnataka History/Political History R (750 - 982) 3.mp4",
    "History/Karnataka History/Political History R(750 - 982) 2.mp4",
    "History/Karnataka History/Political History Vn (1336 - 1649) 1.mp4",
    "History/Karnataka History/Political History Vn 3.mp4",
    "History/Karnataka History/Political History Vn 4.mp4",
    "History/Karnataka History/Rastrakutas.mp4",
    "History/Karnataka History/Tippu Sultan.mp4",
    "History/Karnataka History/Unification Movement In Karnataka.mp4",
    "History/Karnataka History/Vijayanagara Empire (1336 - 1649).mp4",
    "History/Karnataka History/badami chalukyas.mp4",
    "History/Karnataka History/political history of bc 1.mp4",
    "files/Courses/COURSE0002/audios-24c44431-345f-4b4c-be49-e877b9aee6f3/file_example_MP3_700KB.mp3",
    "files/Courses/COURSE0002/pdfs-1d4bf772-f66c-42e3-9864-3584fcb23f0e/table of contant (1).pdf",
    "files/Courses/COURSE0002/video-fdda4e4b-c49d-44d6-8ddd-09801245795e/Insertion at the Beginning of the Linked List.mp4",
    "files/plan.png"
]

# -------------------- VIDEO DURATION HELPER --------------------
# You can implement this using moviepy or ffprobe as per your environment.

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

# -------------------- UTILS --------------------

def is_karnataka_history_video(key: str) -> bool:
    key = key.strip()
    if not key.startswith("History/Karnataka History/"):
        return False
    # Ignore the folder itself
    if key.endswith("/"):
        return False
    # Only video files
    return key.lower().endswith((".mp4", ".m4v"))

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

# -------------------- MAIN LOGIC --------------------

def main():
    course = Course.objects(id=COURSE_DB_ID).first()
    if not course:
        raise ValueError(f"Course with _id={COURSE_DB_ID} not found")

    existing_titles = {ch.video.title for ch in course.chapters if ch.type == "video" and ch.video}

    for key in ALL_S3_KEYS:
        key = key.strip()

        if not is_karnataka_history_video(key):
            continue

        title = key_to_title(key)

        # Avoid duplicates based on title
        if title in existing_titles:
            print(f"Skipping existing chapter: {title}")
            continue

        raw_url = key_to_s3_url(key)
        video_url = replace_with_cloudfront(raw_url)

        duration = get_video_duration_from_url(video_url)

        video_chapter = VideoChapter(
            video_url=video_url,
            thumbnail=COMMON_THUMBNAIL,
            title=title,
            duration=duration or ""  # keep empty if it failed
        )

        chapter = Chapter(
            type="video",
            video=video_chapter,
            demo=False
        )
        chapter.save()

        course.chapters.append(chapter)
        existing_titles.add(title)

        print(f"Created chapter: {title} | URL: {video_url} | Duration: {duration}")

    course.save()
    print("All Karnataka History video chapters added to the course.")

if __name__ == "__main__":
    main()
