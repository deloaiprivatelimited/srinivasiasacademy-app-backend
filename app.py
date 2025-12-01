from flask import Flask, request, session, jsonify
from flask_cors import CORS
from mongoengine import Document,StringField
import logging
from models.college import College

import boto3
import os

from routes.console.parlour import bp as parlour_bp  # Import the parlour_bp Blueprint
from routes.dmq import dmq_bp  # Import the dmq_bp Blueprint
# Custom logger for print statements
# print_logger = logging.getLogger('print_logger')
# print_logger.setLevel(logging.INFO)

# File handler for the print statements
# print_file_handler = logging.FileHandler('print_statements.log')
# print_file_handler.setLevel(logging.INFO)

# Formatter for the log entries
# formatter = logging.Formatter('%(asctime)s - %(message)s')
# print_file_handler.setFormatter(formatter)

# Add the handler to the logger
# print_logger.addHandler(print_file_handler)

# app.py
from flask import Flask
from flask_cors import CORS
from mongoengine import connect
from routes.student import student_bp  # Import the student_bp Blueprint
from models.student import Student  # Import your models
from routes.course import course_bp  # Import the course_bp Blueprint
from routes.tests import test_blueprint
from routes.questions import question_bp 
from dotenv import load_dotenv

load_dotenv()

from routes.package import package_bp
# logging.basicConfig(
#     level=logging.DEBUG,  # Set the log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
#     handlers=[
#         logging.FileHandler("app.log")  # Log to a file named 'app.log'
#     ]
# )
# logger = logging.getLogger(__name__)  # Create a logger object




app = Flask(__name__)


app.secret_key = 'your_secret_key'
CORS(app, resources={r"/*": {"origins": "*"}})
# MongoDB configuration

app.config['MONGODB_SETTINGS'] = {
     'db': 'azad',  # Replace with your database name
     'host': 'mongodb://localhost:27017'  # Local MongoDB URI
 }
connect(host=os.getenv("MONGO_URI"))
app.register_blueprint(parlour_bp, url_prefix="/console/parlour")  # Register the parlour_bp Blueprint
# Register the student Blueprint
app.register_blueprint(student_bp, url_prefix='/admin/student')
app.register_blueprint(course_bp, url_prefix='/admin/course')
app.register_blueprint(package_bp,url_prefix='/admin/package')
app.register_blueprint(test_blueprint,url_prefix='/admin/test')

app.register_blueprint(question_bp,url_prefix='/admin/question')
app.register_blueprint(dmq_bp, url_prefix='/admin')  # Register the dmq_bp Blueprint
@app.route('/student-login', methods=['POST'])
def student_login():
    data = request.get_json()
    email_id = data.get('email_id')
    password = data.get('password')
    ip_address = data.get('ip_address', '')
    # logger.info(f'Login attempt - Email: {email_id}, Password: {password}, IP Address: {ip_address}')
    # print_logger.info(f'Login attempt - Email: {email_id}, Password: {password}, IP Address: {ip_address}')

    student = Student.objects(email_id=email_id, password=password).first()
    # print_logger.info(f'Srudent {student} resytlt')
    if student:
        print(student)
        # logger.info(f'Student {email_id} found in database')
        # print_logger.info(f'Login attempt2 - Email: {email_id}, Password: {password}, IP Address: {ip_address}')
        
        print(student.ip_address)
        if student.ip_address == 'NA' or student.ip_address == ip_address or ip_address == '':
            if student.ip_address == 'NA' or student.ip_address == '':
                student.ip_address = ip_address
                student.save()
            return jsonify(student.to_json_students()), 200
        else:
            return jsonify(student.to_json_students()), 200
#            return jsonify({"error": "IP address does not match the registered device"}), 403
    else:
        return jsonify({"error": "Invalid email or password"}), 401

from models.course import Course
@app.route('/students/courses', methods=['GET'])
def get_all_courses_students():
    try:
        # Get limit and offset from request arguments, with default values
        limit = int(request.args.get('limit', 10))
        offset = int(request.args.get('offset', 0))
        
        # Fetch the courses from the database with pagination
        courses = Course.list_courses(limit=limit, offset=offset)
        
        # Convert the courses to JSON format
        courses_json = [course.to_json_students() for course in courses]
        
        # Return the JSON response
        return jsonify(courses_json), 200
    except Exception as e:
        print(e)
        return jsonify({'error': str(e)}), 500

@app.route('/app/home-content', methods=['GET'])
def home_content():
    data = {
        "heroImages": [
            "https://srinivas-ias-academy.s3.amazonaws.com/uploads/srinivas_ias_Academy_logo.jpeg",
            "https://srinivas-ias-academy.s3.amazonaws.com/uploads/SRINIVAS_IAS_ACADEMY.png",
            "https://srinivas-ias-academy.s3.amazonaws.com/uploads/WhatsApp_Image_2025-11-10_at_3.11.41_PM_(1).jpeg",
        ],

        "latestUpdates": [
            {
                "label": "UPSC Civil Services (Preliminary) Exam 2025 Notification Released",
                "url": "https://upsc.gov.in/examinations/Civil%20Services%20(Preliminary)%20Examination,%20%202025"
            },
            {
                "label": "UPSC Civil Services (Main) Examination 2025 — Timetable & Admit Card",
                "url": "https://upsc.gov.in/examinations/Civil%20Services%20(Main)%20Examination,%202025"
            },
            {
                "label": "KPSC KAS Recruitment 2025 — Mains Result Announcement Soon",
                "url": "https://testbook.com/kpsc-kas"
            }
        ]

    }

    return jsonify(data), 200


from models.package import Package
@app.route('/students/packages', methods=['GET'])
def get_all_packages_students():
    try:
        # Get limit and offset from request arguments, with default values
        limit = int(request.args.get('limit', 10))
        offset = int(request.args.get('offset', 0))
        
        # Fetch the courses from the database with pagination
        courses = Package.list_packages(limit=limit, offset=offset)
        
        # Convert the courses to JSON format
        courses_json = [course.to_json_students() for course in courses]
        
        # Return the JSON response
        return jsonify(courses_json), 200
    except Exception as e:
        print(e)
        return jsonify({'error': str(e)}), 500

@app.route('/students/<student_id>/enrolled_cp' , methods =['GET'])
def get_enrolled_cp(student_id):
    try:
        student = Student.objects(id=student_id).first()
        courses =[course.to_json_students() for course in student.courses_enrolled]
        packages =[package.to_json_students() for package in student.packages_enrolled]
#        tests = [test.to_json_students() for test in student.tests]
        tests = [
    test.to_json_students() 
    for test in sorted(student.tests, key=lambda t: t.order_index)
]
        return jsonify(
            {
                "courses" :courses,
                "packages" : packages,
                "tests":tests,
            }
        )
    except Exception as e:
        print(e)
        return jsonify({'error': str(e)}), 500
    
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if email == 'admin@azadicsacademy.com' and password == 'Azad@0000':
        session['user'] = email
        return jsonify({'message': 'Login successful!','success':True}), 200
@app.route('/test_app', methods=['GET'])
def test1():
    return jsonify({'message': 'Login successful!','success':True}), 200


@app.route('/student-signup', methods=['POST'])
def student_signup():
    try:
        data = request.get_json()

        name = data.get('name')
        contact_number = data.get('contact_number')
        email_id = data.get('email_id')
        password = data.get('password')
        ip_address = data.get('ip_address', 'NA')

        if not all([name, contact_number, email_id, password]):
            return jsonify({"error": "All required fields must be provided"}), 400

        # Create new student
        student = Student.add_student(
            name=name,
            contact_number=contact_number,
            email_id=email_id,
            password=password,
            ip_address=ip_address
        )

        return jsonify({
            "message": "Student created successfully",
            "student": student.to_json_students()
        }), 201

    except ValueError as ve:
        # Handles duplicate errors (email or contact already exists)
        return jsonify({"error": str(ve)}), 409

    except Exception as e:
        print(e)
        return jsonify({"error": "Internal server error"}), 500

@app.route('/logout', methods=['POST'])
def logout():
    session.pop('user', None)
    return jsonify({'message': 'You have been logged out.'}), 200








# Configure boto3 client
s3_client = boto3.client(
    's3',
    region_name=os.getenv('AWS_REGION'),  # e.g., 'us-east-1'
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
)

@app.route('/generate-presigned-url', methods=['POST'])
def generate_presigned_url():
    data = request.get_json()
    file_name = data.get('fileName')
    file_type = data.get('fileType')
    path = data.get('path', '').lstrip('/')

    if not file_name or not file_type:
        return jsonify({'error': 'Missing fileName or fileType'}), 400

    key = f'files/{path}/{file_name}' if path else f'files/{file_name}'

    try:
        presigned_url = s3_client.generate_presigned_url(
            'put_object',
            Params={
                'Bucket': 'azad',
                'Key': key,
                'ContentType': file_type,
            },
            ExpiresIn=600  # URL valid for 60 seconds
        )
        return jsonify({'uploadUrl': presigned_url, 'key': key})
    except Exception as e:
        print("Error generating URL:", e)
        return jsonify({'error': 'Failed to generate presigned URL'}), 500
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
