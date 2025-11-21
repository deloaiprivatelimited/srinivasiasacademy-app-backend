from mongoengine import Document, StringField, ListField, ReferenceField, DecimalField, IntField, connect
from models.chapter import replace_with_cloudfront
from models.chapter import Chapter
# Define a document for counting course IDs
class CourseCounters(Document):
    max_course_id = IntField(default=0)

class Course(Document):
    meta = {'collection': 'courses'}  # MongoDB collection name

    # Attributes
    name = StringField(required=True)
    topics = ListField(StringField())
    professors = ListField(StringField())
    price = DecimalField(precision=2, required=True)  # Assuming price is stored as a decimal number
    whole_duration = StringField(default=0) # Example: "6 months", "1 year", etc.
    chapters = ListField(ReferenceField('Chapter'))
    thumbnail_url = StringField()  # URL to the course thumbnail
    course_id = StringField(unique=True)  # Identifier for the course, unique
    students_enrolled = ListField(ReferenceField('Student'))  # List of students enrolled in the course

    # Methods

    @classmethod
    def add_course(cls, name, topics, professors, price, whole_duration, thumbnail_url):
        # Fetch the current max course_id from the Counters document
        counter_doc = CourseCounters.objects.first()
        if counter_doc:
            max_course_id = counter_doc.max_course_id + 1
        else:
            max_course_id = 1  # Start from 1 if no counters exist

        course_id = f'COURSE{max_course_id:04}'  # Adjust format as needed

        # Create the course
        course = cls(
            name=name,
            topics=topics,
            professors=professors,
            price=price,
            whole_duration=whole_duration,
            thumbnail_url=thumbnail_url,
            course_id=course_id
        )
        course.save()

        # Update the Counters document with the new max_course_id
        if counter_doc:
            counter_doc.update(set__max_course_id=max_course_id)
        else:
            CourseCounters(max_course_id=max_course_id).save()

        return course

    @classmethod
    def delete_course(cls, course_id):
        course = cls.objects(course_id=course_id).first()
        if course:
            course.delete()
            return True
        return False

    @classmethod
    def list_courses(cls, limit=10, offset=0):
        return cls.objects.skip(offset).limit(limit)

    @classmethod
    def get_course_by_id(cls, course_id):
        return cls.objects(course_id=course_id).first()

    @classmethod
    def edit_course(cls, course_id, **kwargs):
        course = cls.objects(course_id=course_id).first()
        if course:
            for field, value in kwargs.items():
                if hasattr(course, field):
                    setattr(course, field, value)
            course.save()
            return course
        return None
    @classmethod
    def add_student(cls, course_id, student_id):
        from models.student import Student
        # Find the course by its ID
        course = cls.objects(course_id=course_id).first()
        if course:
            # Find the student by its ID
            student = Student.objects(id=student_id).first()
            # print(student.courses_enrolled[0].name)
            if student:
                # Add the student to the enrolled list if not already enrolled
                if student not in course.students_enrolled:
                    course.students_enrolled.append(student)
                    course.save()
                    return True
                else:
                    return False  # Student is already enrolled
            else:
                raise ValueError("Student not found")
        else:
            raise ValueError("Course not found")
    def to_json(self):
        json_data = {
            "id": str(self.id),
            "name": self.name,
            "topics": self.topics,
            "professors": self.professors,
            "price": float(self.price),
            "whole_duration": self.whole_duration,
            "chapters": [chapter.to_json() for chapter in self.chapters],
            "thumbnail_url": replace_with_cloudfront(self.thumbnail_url),
            "course_id": self.course_id,
            "students_enrolled": [student.to_json_withoutcourse() for student in self.students_enrolled]
        }
        return json_data

    def to_json_admin(self):
        json_data = {
            "id": str(self.id),
            "name": self.name,
            "topics": self.topics,
            "professors": self.professors,
            "price": float(self.price),
            "whole_duration": self.whole_duration,
            # "chapters": [chapter.to_json() for chapter in self.chapters],
            "thumbnail_url": replace_with_cloudfront(self.thumbnail_url),
            "course_id": self.course_id,
            # "students_enrolled": [student.to_json_withoutcourse() for student in self.students_enrolled]
        }
        return json_data
    
    def to_json_students(self):
        json_data = {
            "id": str(self.id),
            "name": self.name,
            "topics": self.topics,
            "professors": self.professors,
            "price": float(self.price),
            "whole_duration": self.whole_duration,
        "chapters": [chapter.to_json() for chapter in self.chapters if chapter.type != 'live_class'],
            "thumbnail_url": replace_with_cloudfront(self.thumbnail_url),
            "course_id": self.course_id,
        }
        return json_data

