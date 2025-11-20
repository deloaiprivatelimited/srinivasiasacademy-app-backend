from flask import Blueprint, request, jsonify
from models.student import Student  # Correct import path

# Create a Blueprint for student routes
student_bp = Blueprint('student_bp', __name__)

# Route for listing all students
@student_bp.route('/students', methods=['GET'])
def list_students():
    students = Student.list_all_students()
    students_json = [student.to_json_admin() for student in students]
    return jsonify(students_json), 200

@student_bp.route('/students', methods=['POST'])
def add_student():
    data = request.get_json()
    name = data.get('name')
    contact_number = data.get('contact_number')
    email_id = data.get('email_id')
    ip_address = data.get('ip_address')
    password = data.get('password')

    try:
        student = Student.add_student(name, contact_number, email_id, ip_address, password)
        return jsonify(student.to_json()), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

from models.course import Course
from models.enrollment_details import EnrollmentDetails
@student_bp.route('/students/<student_id>/enrol/<course_id>', methods=['PUT'])
def enrol_student(student_id, course_id):
    try:
        print("yes")
        # Fetch the student and course
        student = Student.objects(id=student_id).first()
        course = Course.objects(id=course_id).first()
        print(student)
        print(course)
        if not student:
            return jsonify({'error': 'Student not found'}), 404

        if not course:
            return jsonify({'error': 'Course not found'}), 404
        
        # Get number of days from request data
        data = request.get_json()
        number_of_days = data.get('number_of_days')
        print(number_of_days)
        print(str(student_id))
        print([str(c.id) for c in course.students_enrolled])
        print(str(course_id))
        print([str(c.id) for c in student.courses_enrolled])
        # Check if student is already enrolled in the course
        if str(student_id) not in [str(c.id) for c in course.students_enrolled] and \
           str(course_id) not in [str(c.id) for c in student.courses_enrolled]:
            print("yes came in")
            student.courses_enrolled.append(course)
            course.students_enrolled.append(student)
            student.save()
            course.save()
            # Create enrollment details
            enrollment = EnrollmentDetails(
                student_id=student,
                course_id=course,
                number_of_days=number_of_days
            )
            enrollment.save()

            return jsonify({'message': 'Student enrolled successfully'}), 200
        else:
            return jsonify({'error': 'Student is already enrolled in this course'}), 400

    except Exception as e:
        # Log the exception (you might want to use a proper logging mechanism)
        print(f"An error occurred: {e}")

        # Return a generic error response
        return jsonify({'error': 'An unexpected error occurred'}), 500




from models.course import Course
from models.enrollment_details import EnrollmentDetails
from models.package import Package
from models.package_ernollment_Details import PackageEnrollmentDetails
@student_bp.route('/students/<student_id>/enrolpackage/<course_id>', methods=['PUT'])
def package_enrol_student(student_id, course_id):
    try:
        print("yes")
        # Fetch the student and course
        student = Student.objects(id=student_id).first()
        course = Package.objects(id=course_id).first()
        print(student)
        print(course)
        if not student:
            return jsonify({'error': 'Student not found'}), 404

        if not course:
            return jsonify({'error': 'Course not found'}), 404
        
        # Get number of days from request data
        data = request.get_json()
        number_of_days = data.get('number_of_days')
        print(number_of_days)
        print(str(student_id))
        print([str(c.id) for c in course.students_enrolled])
        print(str(course_id))
        print([str(c.id) for c in student.courses_enrolled])
        # Check if student is already enrolled in the course
        if str(student_id) not in [str(c.id) for c in course.students_enrolled] and \
           str(course_id) not in [str(c.id) for c in student.packages_enrolled]:
            print("yes came in")
            student.packages_enrolled.append(course)
            course.students_enrolled.append(student)
            
            # Create enrollment details
            enrollment = PackageEnrollmentDetails(
                student_id=student,
                package_id=course,
                number_of_days=number_of_days
            )
            student.save()
            course.save()
            enrollment.save()

            return jsonify({'message': 'Student enrolled successfully'}), 200
        else:
            return jsonify({'error': 'Student is already enrolled in this course'}), 400

    except Exception as e:
        # Log the exception (you might want to use a proper logging mechanism)
        print(f"An error occurred: {e}")

        # Return a generic error response
        return jsonify({'error': 'An unexpected error occurred'}), 500

@student_bp.route('/students/<student_id>/unenrol/<course_id>', methods=['PUT'])
def unenrol_student(student_id, course_id):
    # Fetch the student and course
    student = Student.objects(id=student_id).first()
    course = Course.objects(course_id=course_id).first()

    if not student:
        return jsonify({'error': 'Student not found'}), 404

    if not course:
        return jsonify({'error': 'Course not found'}), 404

    # Check if the student is enrolled in the course
    print(course.id)
    print([str(c.id) for c in student.courses_enrolled])
    print(str(student_id))
    print([str(s.id) for s in course.students_enrolled])
    if str(course.id) in [str(c.id) for c in student.courses_enrolled] and \
       str(student_id) in [str(s.id) for s in course.students_enrolled]:
        print("Yes")

        student.courses_enrolled = [c for c in student.courses_enrolled if str(c.id) != str(course.id)]
        course.students_enrolled = [s for s in course.students_enrolled if str(s.id) != str(student_id)]
        EnrollmentDetails.objects(student_id=student, course_id=course).delete()

        student.save()
        course.save()

        return jsonify({'message': 'Student unenrolled successfully'}), 200
    else:
        return jsonify({'error': 'Student is not enrolled in this course'}), 400


@student_bp.route('/students/<student_id>/unenrolpackage/<course_id>', methods=['PUT'])
def package_unenrol_student(student_id, course_id):
    # Fetch the student and course
    student = Student.objects(id=student_id).first()
    course = Package.objects(package_id=course_id).first()

    if not student:
        return jsonify({'error': 'Student not found'}), 404

    if not course:
        return jsonify({'error': 'Course not found'}), 404

    # Check if the student is enrolled in the course
    print(course.id)
    print([str(c.id) for c in student.packages_enrolled])
    print(str(student_id))
    print([str(s.id) for s in course.students_enrolled])
    if str(course.id) in [str(c.id) for c in student.packages_enrolled] and \
       str(student_id) in [str(s.id) for s in course.students_enrolled]:
        print("Yes")

        student.packages_enrolled = [c for c in student.packages_enrolled if str(c.id) != str(course.id)]
        course.students_enrolled = [s for s in course.students_enrolled if str(s.id) != str(student_id)]
        PackageEnrollmentDetails.objects(student_id=student, package_id=course).delete()

        student.save()
        course.save()

        return jsonify({'message': 'Student unenrolled successfully'}), 200
    else:
        return jsonify({'error': 'Student is not enrolled in this course'}), 400

@student_bp.route('/students/<student_id>', methods=['DELETE'])
def delete_student(student_id):
    student = Student.get_student_by_id(student_id)
    if not student:
        return jsonify({'error': 'Student not found'}), 404

    # Unenroll the student from all courses
    for course in student.courses_enrolled:
        unenrol_student(student_id, course_id=course.course_id)
    for package in student.packages_enrolled:
        package_enrol_student(student_id=student_id , package_id = package.package_id)
    # Now delete the student
    Student.delete_student(student_id)
    return jsonify({'message': 'Student deleted successfully'}), 200

# Route for editing a student
@student_bp.route('/students/<student_id>', methods=['PUT'])
def edit_student(student_id):
    data = request.get_json()
    student = Student.get_student_by_id(student_id)
    if not student:
        return jsonify({'error': 'Student not found'}), 404

    Student.edit_student(student_id, **data)
    student.reload()  # Reload student object to reflect changes
    return jsonify(student.to_json()), 200


# Route for resetting IP address
@student_bp.route('/students/<student_id>/reset_ip', methods=['PUT'])
def reset_ip(student_id):
    student = Student.get_student_by_id(student_id)
    if not student:
        return jsonify({'error': 'Student not found'}), 404

    student.ip_address = 'NA'
    student.save()
    return jsonify(student.to_json()), 200

# Route for changing the password
@student_bp.route('/students/<student_id>/change_password', methods=['PUT'])
def change_password(student_id):
    data = request.get_json()
    new_password = data.get('new_password')
    
    student = Student.get_student_by_id(student_id)
    if not student:
        return jsonify({'error': 'Student not found'}), 404

    if not new_password:
        return jsonify({'error': 'New password is required'}), 400

    student.password = new_password
    student.save()
    return jsonify(student.to_json()), 200


# Route for getting a student by ID
@student_bp.route('/students/<student_id>', methods=['GET'])
def get_student(student_id):
    student = Student.get_student_by_id(student_id)
    if not student:
        return jsonify({'error': 'Student not found'}), 404

    return jsonify(student.to_json()), 200

@student_bp.route('/enrollment-details/<string:student_id>', methods=['GET'])
def get_enrollment_details(student_id):
    try:
        details = EnrollmentDetails.get_enrollment_details(student_id)
        return jsonify(details), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@student_bp.route('/students/<student_id>/update_enrollment/<course_id>', methods=['PUT'])
def update_enrollment_days(student_id, course_id):
    data = request.get_json()
    additional_days = data.get('additional_days')

    if additional_days is None or not isinstance(additional_days, int):
        return jsonify({'error': 'Invalid input for additional days'}), 400

    enrollment = EnrollmentDetails.objects(student_id=student_id, course_id=course_id).first()

    if not enrollment:
        return jsonify({'error': 'Enrollment not found'}), 404

    enrollment.number_of_days += additional_days
    enrollment.save()

    return jsonify({'message': 'Number of days updated successfully!', 'new_number_of_days': enrollment.number_of_days})


from models.package_ernollment_Details import PackageEnrollmentDetails

@student_bp.route('/package-enrollment-details/<string:student_id>', methods=['GET'])
def get_package_enrollment_details(student_id):
    try:
        details = PackageEnrollmentDetails.get_enrollment_details(student_id)
        return jsonify(details), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@student_bp.route('/students/<student_id>/update_package_enrollment/<package_id>', methods=['PUT'])
def update_package_enrollment_days(student_id, package_id):
    data = request.get_json()
    additional_days = data.get('additional_days')

    if additional_days is None or not isinstance(additional_days, int):
        return jsonify({'error': 'Invalid input for additional days'}), 400

    enrollment = PackageEnrollmentDetails.objects(student_id=student_id, package_id=package_id).first()

    if not enrollment:
        return jsonify({'error': 'Enrollment not found'}), 404

    enrollment.number_of_days += additional_days
    enrollment.save()

    return jsonify({'message': 'Number of days updated successfully!', 'new_number_of_days': enrollment.number_of_days})
