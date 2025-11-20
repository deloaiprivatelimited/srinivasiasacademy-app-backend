from mongoengine import Document, StringField, DateTimeField, IntField

class DMQ(Document):
    meta = {'collection': 'dmq'}  # MongoDB collection name
    
    questions = StringField(required=True)  # Question text
    date = DateTimeField(required=True)     # When this DMQ is scheduled or created
    category = StringField(required=True)   # Category name
    time = StringField(required=True)       # Could store as HH:MM or descriptive string
    marks = IntField(required=True)         # Points or score for the question
    
    def to_json(self):
        return {
            "id": str(self.id),
            "questions": self.questions,
            "date": self.date.isoformat() if self.date else None,
            "category": self.category,
            "time": self.time,
            "marks": self.marks
        }
