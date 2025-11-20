from mongoengine import Document, StringField, ListField, ReferenceField, DecimalField, IntField

from models.course import Course
from models.student import Student

# Define a document for counting package IDs
class PackageCounters(Document):
    max_package_id = IntField(default=0)

class Package(Document):
    meta = {'collection': 'packages'}  # MongoDB collection name

    # Attributes
    name = StringField(required=True)
    topics = ListField(StringField())
    professors = ListField(StringField())
    price = DecimalField(precision=2, required=True)  # Assuming price is stored as a decimal number
    courses = ListField(ReferenceField(Course) ,default=[])
    thumbnail_url = StringField()  # URL to the package thumbnail
    package_id = StringField(unique=True)  # Identifier for the package, unique
    students_enrolled = ListField(ReferenceField(Student),default=[])  # List of students enrolled in the package

    # Methods

    @classmethod
    def add_package(cls, name, topics, professors, price, thumbnail_url):
        # Fetch the current max package_id from the Counters document
        counter_doc = PackageCounters.objects.first()
        if counter_doc:
            max_package_id = counter_doc.max_package_id + 1
        else:
            max_package_id = 1  # Start from 1 if no counters exist

        package_id = f'PACKAGE{max_package_id:04}'  # Adjust format as needed

        # Create the package
        package = cls(
            name=name,
            topics=topics,
            professors=professors,
            price=price,
            thumbnail_url=thumbnail_url,
            package_id=package_id
        )
        package.save()

        # Update the Counters document with the new max_package_id
        if counter_doc:
            counter_doc.update(set__max_package_id=max_package_id)
        else:
            PackageCounters(max_package_id=max_package_id).save()

        return package

    @classmethod
    def delete_package(cls, package_id):
        package = cls.objects(package_id=package_id).first()
        if package:
            package.delete()
            return True
        return False

    @classmethod
    def list_packages(cls, limit=10, offset=0):
        return cls.objects.skip(offset).limit(limit)

    @classmethod
    def get_package_by_id(cls, package_id):
        return cls.objects(package_id=package_id).first()

    @classmethod
    def edit_package(cls, package_id, **kwargs):
        package = cls.objects(package_id=package_id).first()
        if package:
            for field, value in kwargs.items():
                if hasattr(package, field):
                    setattr(package, field, value)
            package.save()
            return package
        return None

    @classmethod
    def add_student(cls, package_id, student_id):
        # Find the package by its ID
        package = cls.objects(package_id=package_id).first()
        if package:
            # Find the student by its ID
            student = Student.objects(id=student_id).first()
            if student:
                # Add the student to the enrolled list if not already enrolled
                if student not in package.students_enrolled:
                    package.students_enrolled.append(student)
                    package.save()
                    return True
                else:
                    return False  # Student is already enrolled
            else:
                raise ValueError("Student not found")
        else:
            raise ValueError("Package not found")

    def to_json(self):
        json_data = {
            "id": str(self.id),
            "name": self.name,
            "topics": self.topics,
            "professors": self.professors,
            "price": float(self.price),
            "courses": [course.to_json() for course in self.courses],
            "thumbnail_url": self.thumbnail_url,
            "package_id": self.package_id,
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
            # "courses": [course.to_json() for course in self.courses],
            "thumbnail_url": self.thumbnail_url,
            "package_id": self.package_id,
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
            "courses": [course.to_json_students() for course in self.courses],
            "thumbnail_url": self.thumbnail_url,
            "package_id": self.package_id,
        }
        return json_data
