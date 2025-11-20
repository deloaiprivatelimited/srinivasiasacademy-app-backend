from flask import Blueprint, request, jsonify
from mongoengine import connect, DoesNotExist
from models.package import Package, PackageCounters

# Initialize Flask blueprint
package_bp = Blueprint('package_bp', __name__)

from models.course import Course
@package_bp.route('/packages', methods=['POST'])
def add_package():
    try:
        # Extract data from the request
        data = request.get_json()
        name = data.get('name')
        topics = data.get('topics', [])
        professors = data.get('professors', [])
        price = data.get('price')
        thumbnail_url = data.get('thumbnail_url', '')

        # Convert course IDs to Course references

        # Add the package
        package = Package.add_package(
            name=name,
            topics=topics,
            professors=professors,
            price=price,
            thumbnail_url=thumbnail_url
        )

        return jsonify({"message": "Package added successfully", "package": package.to_json()}), 201
    except Exception as e:
        print(str(e))
        return jsonify({"error": str(e)}), 400




@package_bp.route('/packages', methods=['GET'])
def get_packages():
    try:
        # Fetch all packages from the database
        packages = Package.objects()
        packages_json = [package.to_json_admin() for package in packages]
        print("nnn")
        return jsonify(packages_json), 200
    except Exception as e:
        print(str(e))


        return jsonify({"error": str(e)}), 400
    

@package_bp.route('/packages/<package_id>', methods=['GET'])
def get_package_by_id(package_id):
    try:
        package = Package.objects.get(package_id=package_id)
        return jsonify(package.to_json()), 200
    except DoesNotExist:
        return jsonify({"error": "Package not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@package_bp.route('/packages/<package_id>', methods=['PUT'])
def edit_package(package_id):
    try:
        # Extract data from the request
        data = request.get_json()
        name = data.get('name')
        topics = data.get('topics', [])
        professors = data.get('professors', [])
        price = data.get('price')
        thumbnail_url = data.get('thumbnail_url', '')

        # Find the package
        package = Package.objects.get(package_id=package_id)

        # Update the package fields
        package.name = name
        package.topics = topics
        package.professors = professors
        package.price = price
        package.thumbnail_url = thumbnail_url

        # Save the package
        package.save()

        return jsonify({"message": "Package updated successfully", "package": package.to_json()}), 200
    except DoesNotExist:
        return jsonify({"error": "Package not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 400
@package_bp.route('/<package_id>/add_course/<course_id>',methods=['POST'])
def add_course_to_package(package_id,course_id):
    try:
        package =Package.objects(id=package_id).first()
        course=Course.objects(id=course_id).first()
        if str(course_id) not in [str(c.id) for c in package.courses]:
            package.courses.append(course)
            package.save()
            return jsonify({'message': 'Course added successfully'}), 200

        else:
            return jsonify({'error': 'Course is already enrolled in this Package'}), 400
 
    except Exception as e:
        return jsonify({'error': 'An unexpected error occurred'}), 500


@package_bp.route('/<package_id>/remove_course/<course_id>',methods=['POST'])
def remove_course_to_package(package_id,course_id):
    try:
        package =Package.objects(id=package_id).first()
        course=Course.objects(id=course_id).first()
        if str(course_id)  in [str(c.id) for c in package.courses]:
            package.courses.remove(course)
            package.save()
            return jsonify({'message': 'Course removed successfully'}), 200

        else:
            return jsonify({'error': 'Course is not enrolled in this Package'}), 400
 
    except Exception as e:
        return jsonify({'error': 'An unexpected error occurred'}), 500


@package_bp.route('/packages/<course_id>', methods=['DELETE'])
def delete_course(course_id):
    print(course_id)
    from routes.student import package_unenrol_student
    course = Package.objects(package_id=course_id).first()

    for student_id in course.students_enrolled:
        package_unenrol_student(student_id=student_id.id, course_id=course_id)
        
    success =Package.delete_package(course_id)
    if success:
        return jsonify({"message": "Course deleted successfully."}), 200
    return jsonify({"message": "Course not found."}), 404
