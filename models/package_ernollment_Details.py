from mongoengine import Document, StringField, ReferenceField, DateTimeField, IntField
from datetime import datetime, timedelta

class PackageEnrollmentDetails(Document):
    meta = {'collection': 'package_enrollment_details'}  # MongoDB collection name

    student_id = ReferenceField('Student', required=True)  # Reference to a Student document
    package_id = ReferenceField('Package', required=True)  # Reference to a Package document
    date_created = DateTimeField(default=datetime.utcnow)  # Date and time when the enrollment was created
    number_of_days = IntField(required=True)  # Number of days for the enrollment

    @classmethod
    def get_enrollment_details(cls, student_id):
        # Fetch all package enrollment details for the given student_id
        enrollments = cls.objects(student_id=student_id)

        # Prepare the details including the expiration date
        enrollment_details = []
        for enrollment in enrollments:
            expiry_date = enrollment.date_created + timedelta(days=enrollment.number_of_days)
            details = {
                'student_id': str(enrollment.student_id.id),
                'package_id': str(enrollment.package_id.id),
                'date_created': enrollment.date_created,
                'number_of_days': enrollment.number_of_days,
                'expiry_date': expiry_date
            }
            enrollment_details.append(details)

        return enrollment_details
