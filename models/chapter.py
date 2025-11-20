from mongoengine import EmbeddedDocument, StringField,BooleanField, EmbeddedDocumentField, ListField, Document, URLField, FloatField
CLOUDFRONT_DOMAIN = "d1ytcm2rfo0yep.cloudfront.net"

def replace_with_cloudfront(url: str) -> str:
    if not url:
        return url
    # Keep the path, replace the domain
    try:
        parts = url.split('/', 3)  # Split into scheme, '', domain, path
        if len(parts) >= 4:
            return f"https://{CLOUDFRONT_DOMAIN}/{parts[3]}"
        else:
            return url
    except:
        return url

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
    thumbnail = URLField(required=False,default='')
    title = StringField(required=True)
    duration = StringField(required=True,default='')  # Example: "10:30" for 10 minutes 30 seconds
    professor = StringField(required=False,default=' ')
    notes = StringField(default='')

class LiveClass(EmbeddedDocument):
    title = StringField(required=True)
    start_date =StringField(required=True)
    start_time = StringField(required=True)
    duration = StringField(required=True)
    link = StringField(default='')

class Chapter(Document):
    meta = {'collection': 'chapters'}  # MongoDB collection name

    type = StringField(required=True, choices=['pdf', 'text', 'video','live_class','audio'])
    pdf = EmbeddedDocumentField(PDFChapter)
    audio = EmbeddedDocumentField(AudioChapter)

    text = EmbeddedDocumentField(TextChapter)
    video = EmbeddedDocumentField(VideoChapter)
    demo = BooleanField(default=False)
    live_class = EmbeddedDocumentField(LiveClass)


   
    def to_json(self):
        json_data = {
            "id": str(self.id),
            "type": self.type,
            "demo": self.demo
        }

        if self.type == 'pdf' and self.pdf:
            json_data.update({
                "pdf": {
                    "title": self.pdf.title,
                    "pdf_url": replace_with_cloudfront(self.pdf.pdf_url),
                    "isPreview": self.demo
                }
            })

        if self.type == 'audio' and self.audio:
            json_data.update({
                "audio": {
                    "title": self.audio.title,
                    "audio_url": replace_with_cloudfront(self.audio.audio_url),
                    "isPreview": self.demo
                }
            })

        elif self.type == 'text' and self.text:
            json_data.update({
                "text": {
                    "title": self.text.title,
                    "text": self.text.text,
                    "isPreview": self.demo
                }
            })

        elif self.type == 'live_class' and self.live_class:
            json_data.update({
                "live_class": {
                    "title": self.live_class.title,
                    "start_date": self.live_class.start_date,
                    "start_time": self.live_class.start_time,
                    "duration": self.live_class.duration,
                    "link": self.live_class.link
                }
            })

        elif self.type == 'video' and self.video:
            json_data.update({
                "video": {
                    "video_url": replace_with_cloudfront(self.video.video_url),
                    "thumbnail": replace_with_cloudfront(self.video.thumbnail) if self.video.thumbnail else "",
                    "title": self.video.title,
                    "duration": self.video.duration,
                    "professor": self.video.professor,
                    "notes": self.video.notes,
                    "isPreview": self.demo
                }
            })

        return json_data