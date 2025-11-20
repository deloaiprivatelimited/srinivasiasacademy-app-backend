from datetime import datetime, timedelta
from mongoengine import Document, StringField, DateTimeField, ReferenceField, ListField,IntField
import json
from bson import ObjectId
from models.course import Course

# Define a document for counting student IDs
class Counters(Document):
    max_student_id = IntField(default=0)
class Student(Document):
    meta = {'collection': 'students'}  # MongoDB collection name

    # Attributes
    name = StringField(required=True)
    contact_number = StringField(unique=True)  # Make contact_number unique
    email_id = StringField(unique=True)  # Make email_id unique
    student_id = StringField(unique=True)
    ip_address = StringField(default='NA')
    password = StringField(required=True)
    date_created = DateTimeField(default=datetime.utcnow)
    courses_enrolled = ListField(ReferenceField('Course'), default=[])
    packages_enrolled = ListField(ReferenceField('Package'), default=[])
    tests = ListField(ReferenceField('Test'), default=[])

    # Methods
    @classmethod
    def add_student(cls, name, contact_number=None, email_id=None, ip_address=None, password=None):
        # Check for existing contact_number or email_id
        if cls.objects(contact_number=contact_number).first():
            raise ValueError("Contact number already exists.")
        if cls.objects(email_id=email_id).first():
            raise ValueError("Email ID already exists.")

        # Fetch the current max student_id from the Counters document
        counter_doc = Counters.objects.first()
        if counter_doc:
            max_student_id = counter_doc.max_student_id + 1
        else:
            max_student_id = 1  # Start from 1 if no counters exist

        student_id = f'STUD{max_student_id:04}'  # Adjust format as needed

        # Create the student
        student = cls(name=name, contact_number=contact_number, email_id=email_id,
                      ip_address=ip_address or 'NA', password=password, student_id=student_id)
        student.save()

        # Update the Counters document with the new max_student_id
        if counter_doc:
            counter_doc.update(set__max_student_id=max_student_id)
        else:
            Counters(max_student_id=max_student_id).save()

        return student

    def enrol_student(self, course_id):
        if course_id not in self.courses_enrolled:
            self.courses_enrolled.append(course_id)
            self.save()

    def unenrol_student(self, course_id):
        if course_id in self.courses_enrolled:
            self.courses_enrolled.remove(course_id)
            self.save()

    @classmethod
    def delete_student(cls, student_id):
        cls.objects(id=student_id).delete()

    @classmethod
    def edit_student(cls, student_id, **kwargs):
        cls.objects(id=student_id).update(**kwargs)

    @classmethod
    def list_all_students(cls):
        return cls.objects()

    @classmethod
    def get_student_by_id(cls, student_id):
        return cls.objects(id=student_id).first()

    def to_json_withoutcourse(self):

        json_data = {
            "id": str(self.id),
            "name": self.name,
            "contact_number": self.contact_number,
            "email_id": self.email_id,
            "student_id": self.student_id,
            "ip_address": self.ip_address,
            "password": self.password,
            "date_created": self.date_created.strftime("%Y-%m-%d %H:%M:%S"),
           
        }

        return json_data
    
 
    def to_json(self):
        from models.enrollment_details import EnrollmentDetails
        from models.package_ernollment_Details import PackageEnrollmentDetails
        courses_info = []
        packages_info =[]
        tests=[]
        for course in self.courses_enrolled:
            enrollment = EnrollmentDetails.objects(student_id=self, course_id=course).first()
            if enrollment:
                enrolled_date = enrollment.date_created
                expiry_date = enrolled_date + timedelta(days=enrollment.number_of_days)
                course_info = course.to_json()
                course_info.update({
                    "enrolled_date": enrolled_date.strftime("%Y-%m-%d %H:%M:%S"),
                    "expiry_date": expiry_date.strftime("%Y-%m-%d %H:%M:%S")
                })
                courses_info.append(course_info)
        for package in self.packages_enrolled:
            enrollment = PackageEnrollmentDetails.objects(student_id=self,package_id=package).first()
            if enrollment:
                enrolled_date = enrollment.date_created
                expiry_date = enrolled_date + timedelta(days=enrollment.number_of_days)
                package_info = package.to_json()
                package_info.update({
                    "enrolled_date": enrolled_date.strftime("%Y-%m-%d %H:%M:%S"),
                    "expiry_date": expiry_date.strftime("%Y-%m-%d %H:%M:%S")
                })
                packages_info.append(package_info)
            



        json_data = {
            "id": str(self.id),
            "name": self.name,
            "contact_number": self.contact_number,
            "email_id": self.email_id,
            "student_id": self.student_id,
            "ip_address": self.ip_address,
            "password": self.password,
            "date_created": self.date_created.strftime("%Y-%m-%d %H:%M:%S"),
            "courses_enrolled": courses_info,
            "packages_enrolled" :packages_info,
#            "tests" :  [test.to_json_students() for test in self.tests]
"tests": [
    test.to_json_students() 
    for test in sorted(self.tests, key=lambda t: t.order_index)
]
        }

        return json_data
    

    
    def to_json_admin(self):
       
        json_data = {
            "id": str(self.id),
            "name": self.name,
            "contact_number": self.contact_number,
            "email_id": self.email_id,
            "student_id": self.student_id,
            "ip_address": self.ip_address,
            # "password": self.password,
            "date_created": self.date_created.strftime("%Y-%m-%d %H:%M:%S"),
            # "courses_enrolled": courses_info,
            # "packages_enrolled" :packages_info,
            # "tests" :  [test.to_json_students() for test in self.tests]
        }

        return json_data
    
    def to_json_students(self):
        from models.enrollment_details import EnrollmentDetails
        from models.package_ernollment_Details import PackageEnrollmentDetails
        courses_info = []
        packages_info =[]
        for course in self.courses_enrolled:
            enrollment = EnrollmentDetails.objects(student_id=self, course_id=course).first()
            if enrollment:
                enrolled_date = enrollment.date_created
                expiry_date = enrolled_date + timedelta(days=enrollment.number_of_days)
                course_info = course.to_json_students()
                course_info.update({
                    "enrolled_date": enrolled_date.strftime("%Y-%m-%d %H:%M:%S"),
                    "expiry_date": expiry_date.strftime("%Y-%m-%d %H:%M:%S")
                })
                courses_info.append(course_info)
        for package in self.packages_enrolled:
            enrollment = PackageEnrollmentDetails.objects(student_id=self,package_id=package).first()
            if enrollment:
                enrolled_date = enrollment.date_created
                expiry_date = enrolled_date + timedelta(days=enrollment.number_of_days)
                package_info = package.to_json_students()
                package_info.update({
                    "enrolled_date": enrolled_date.strftime("%Y-%m-%d %H:%M:%S"),
                    "expiry_date": expiry_date.strftime("%Y-%m-%d %H:%M:%S")
                })
                packages_info.append(package_info)


        json_data = {
            "id": str(self.id),
            "name": self.name,
            "contact_number": self.contact_number,
            "email_id": self.email_id,
            "student_id": self.student_id,
            "ip_address": self.ip_address,
            "password": self.password,
            "date_created": self.date_created.strftime("%Y-%m-%d %H:%M:%S"),
            "courses_enrolled": courses_info,
            "packages_enrolled" :packages_info
        }

        return json_data
    
