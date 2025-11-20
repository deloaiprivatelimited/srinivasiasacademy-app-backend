from mongoengine import Document, StringField, DictField, IntField, FloatField

class Question(Document):
    meta = {'collection': 'questions'}  # MongoDB collection name

    question = StringField(required=True)  # The question text
    question_image = StringField(default=None)  # URL to an image, can be None or null
    option_a = DictField(required=True)  # Option A: {'text': '...', 'image_url': '...'}
    option_b = DictField(required=True)  # Option B: {'text': '...', 'image_url': '...'}
    option_c = DictField(required=True)  # Option C: {'text': '...', 'image_url': '...'}
    option_d = DictField(required=True)  # Option D: {'text': '...', 'image_url': '...'}
    correct_option = IntField(required=True, min_value=0, max_value=3)  # Correct option index (0 to 3)
    crt_ans_score = FloatField(default=3.0)  # Default value for correct answer score
    wrong_ans_score = FloatField(default=-0.25)  # Default value for wrong answer score
    question_type = StringField(default='General')  # The question text


    def to_json(self):
        return {
            "id": str(self.id),
            "question": self.question,
            "question_image": self.question_image,
            "options": {
                "A": self.option_a,
                "B": self.option_b,
                "C": self.option_c,
                "D": self.option_d,
            },
            "correct_option": self.correct_option,
            "crt_ans_score": self.crt_ans_score,
            "wrong_ans_score": self.wrong_ans_score,
            "question_type" : self.question_type
        }
