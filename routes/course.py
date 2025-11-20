# routes/course.py
from flask import Blueprint, request, jsonify
from models.course import Course  # Import your Course model
from models.chapter import Chapter

from flask import Flask, request, jsonify
import boto3
from botocore.exceptions import NoCredentialsError
import uuid
course_bp = Blueprint('course', __name__)


@course_bp.route('/courses', methods=['POST'])
def add_course():
    data = request.json
    course = Course.add_course(
        name=data.get('name'),
        topics=data.get('topics', []),
        professors=data.get('professors', []),
        price=data.get('price'),
        whole_duration=data.get('whole_duration'),
        thumbnail_url=data.get('thumbnail_url')
    )
    return jsonify(course.to_json()), 201
@course_bp.route('/courses/<course_id>', methods=['DELETE'])
def delete_course(course_id):
    from routes.student import unenrol_student
    course = Course.objects(course_id=course_id).first()
    for student_id in course.students_enrolled:
        unenrol_student(student_id=student_id.id, course_id=course_id)
        
    success = Course.delete_course(course_id)
    if success:
        return jsonify({"message": "Course deleted successfully."}), 200
    return jsonify({"message": "Course not found."}), 404

@course_bp.route('/courses', methods=['GET'])
def list_courses():
    limit = int(request.args.get('limit', 10))
    offset = int(request.args.get('offset', 0))
    courses = Course.list_courses(limit=limit, offset=offset)
    return jsonify([course.to_json_admin() for course in courses]), 200

@course_bp.route('/courses/<course_id>', methods=['GET'])
def get_course_by_id(course_id):
    course = Course.get_course_by_id(course_id)
    if course:
        return jsonify(course.to_json()), 200
    return jsonify({"message": "Course not found."}), 404

@course_bp.route('/courses/<course_id>', methods=['PUT'])
def edit_course(course_id):
    data = request.json
    updated_course = Course.edit_course(course_id, **data)
    if updated_course:
        return jsonify(updated_course.to_json()), 200
    return jsonify({"message": "Course not found."}), 404



@course_bp.route('/admin/course/courses/<course_id>', methods=['PUT'])
def update_course(course_id):
    data = request.get_json()
    course = Course.objects(course_id=course_id).first()

    if not course:
        return jsonify({'message': 'Course not found'}), 404

    # Update course details
    course.update(
        name=data.get('name', course.name),
        topics=data.get('topics', course.topics),
        professors=data.get('professors', course.professors),
        price=data.get('price', course.price),
        whole_duration=data.get('whole_duration', course.whole_duration),
        chapters=data.get('chapters', course.chapters)  # Update chapters
    )
    return jsonify({'message': 'Course updated successfully!'})


# @course_bp.route('/<course_id>/chapters', methods=['POST'])
# def add_chapter_to_course(course_id):
#     data = request.json
#     print(data)
#     course = Course.get_course_by_id(course_id)
#     if not course:
#         return jsonify({"message": "Course not found."}), 404

#     # Validate chapter type
#     chapter_type = data.get('type')
#     if chapter_type not in ['pdf', 'text', 'video']:
#         return jsonify({"message": "Invalid chapter type."}), 400

#     # Create chapter based on type
#     chapter_data = {"type": chapter_type}
#     if chapter_type == 'pdf':
#         chapter_data['pdf'] = data.get('pdf')
#     elif chapter_type == 'text':
#         chapter_data['text'] = data.get('text')
#     elif chapter_type == 'video':
#         chapter_data['video'] = data.get('video')

#     # Create and save chapter
#     chapter = Chapter(**chapter_data)
#     chapter.save()

#     # Add chapter to the course
#     course.chapters.append(chapter)
#     course.save()

#     return jsonify({
#         "message": "Chapter added successfully.",
#         "chapter": "chapter.to_json()"
#     }), 201

@course_bp.route('/<course_id>/chapters', methods=['POST'])
def add_chapter_to_course(course_id):
    data = request.json
    print(data)
    course = Course.get_course_by_id(course_id)
    if not course:
        return jsonify({"message": "Course not found."}), 404

    # Validate chapter type
    chapter_type = data.get('type')
    if chapter_type not in ['pdf', 'text', 'video' , 'live_class' ,'audio']:
        return jsonify({"message": "Invalid chapter type."}), 400

    # Initialize chapter_data
    chapter_data = {"type": chapter_type}
    
    # Initialize isPreview variable
    is_preview = None
    
    # Process chapter type and remove isPreview
    if chapter_type == 'pdf':
        chapter_pdf = data.get('pdf')
        if 'isPreview' in chapter_pdf:
            is_preview = chapter_pdf.pop('isPreview')
        chapter_data['pdf'] = chapter_pdf
    elif chapter_type == 'audio':
        chapter_pdf = data.get('audio')
        if 'isPreview' in chapter_pdf:
            is_preview = chapter_pdf.pop('isPreview')
        chapter_data['audio'] = chapter_pdf

    elif chapter_type == 'text':
        chapter_text = data.get('text')
        if 'isPreview' in chapter_text:
            is_preview = chapter_text.pop('isPreview')
        chapter_data['text'] = chapter_text

    elif chapter_type == 'video':
        chapter_video = data.get('video')
        if 'isPreview' in chapter_video:
            is_preview = chapter_video.pop('isPreview')
        if not chapter_video.get('thumbnail'):
        # Assign course thumbnail URL to chapter video thumbnail
            chapter_video['thumbnail'] = course.thumbnail_url
        
        chapter_data['video'] = chapter_video

    elif chapter_type == 'live_class':
        chapter_live_class = data.get('live_class')
        chapter_data['live_class'] = chapter_live_class
    # Print the is_preview variable to check its value


    # Print the is_preview variable to check its value
    print(f'is_preview: {is_preview}')

    # Create and save chapter
    
    chapter = Chapter(**chapter_data)
    chapter.demo = is_preview
    chapter.save()

    # # Add chapter to the course
    course.chapters.append(chapter)
    course.save()
    # print(chapter_data)
    return jsonify({
        "message": "Chapter added successfully.",
        # "chapter": chapter.to_json(),
        "isPreview": is_preview
    }), 201

@course_bp.route('/<course_id>/chapters', methods=['PUT'])
def update_chapters(course_id):
    data = request.json
    print(data)
    course = Course.get_course_by_id(course_id)
    if not course:
        return jsonify({"message": "Course not found."}), 404

    chapter_ids = data.get('chapter_ids', [])
    if not isinstance(chapter_ids, list):
        return jsonify({"message": "Invalid data format."}), 400

    # Fetch Chapter documents
    chapters = Chapter.objects(id__in=chapter_ids)
    if len(chapters) != len(chapter_ids):
        return jsonify({"message": "Some chapter IDs are invalid."}), 400

    # Create a dictionary to map chapter IDs to Chapter objects
    chapter_map = {str(chapter.id): chapter for chapter in chapters}

    # Reorder the chapters based on chapter_ids
    ordered_chapters = [chapter_map[id] for id in chapter_ids if id in chapter_map]

    # Update the course with the ordered chapters
    course.chapters = ordered_chapters
    course.save()

    return jsonify({
        "message": "Chapters updated successfully.",
        "course": course.to_json()
    }), 200




@course_bp.route('/courses/<course_id>/chapters/<chapter_id>', methods=['DELETE'])
def delete_chapter_from_course(course_id, chapter_id):
    course = Course.get_course_by_id(course_id)
    if not course:
        return jsonify({"message": "Course not found."}), 404

    # Find and remove the chapter from the course
    chapter = Chapter.objects(id=chapter_id).first()
    if not chapter:
        return jsonify({"message": "Chapter not found."}), 404

    # Remove the chapter from the course's chapters list
    if chapter in course.chapters:
        course.chapters.remove(chapter)
        course.save()

        # Delete the chapter document
        chapter.delete()

        return jsonify({"message": "Chapter deleted successfully."}), 200
    else:
        return jsonify({"message": "Chapter not found in the course."}), 404


@course_bp.route('/edit_chapter/<chapter_id>', methods=['GET', 'POST'])
def edit_chapter(chapter_id):
    if request.method == 'GET':
        try:
            chapter = Chapter.objects.get(id=chapter_id)
            return jsonify(chapter.to_json()), 200
        except Chapter.DoesNotExist:
            return jsonify({"error": "Chapter not found"}), 404

    elif request.method == 'POST':
        data = request.json
        try:
            chapter = Chapter.objects.get(id=chapter_id)
            chapter.demo =data.get('isPreview' ,chapter.demo)

            if chapter.type == 'pdf':
                chapter.pdf.title = data.get('title', chapter.pdf.title)
            elif chapter.type == 'audio':
                chapter.audio.title = data.get('title', chapter.audio.title)
            elif chapter.type == 'text':
                chapter.text.title = data.get('title', chapter.text.title)
                chapter.text.text = data.get('text', chapter.text.text)
            elif chapter.type == 'video':
                chapter.video.title = data.get('title', chapter.video.title)
                chapter.video.duration = data.get('duration', chapter.video.duration)
                chapter.video.professor = data.get('professor', chapter.video.professor)
                chapter.video.notes = data.get('notes', chapter.video.notes)

            chapter.save()
            return jsonify({"message": "Chapter updated successfully"}), 200
        except Chapter.DoesNotExist:
            return jsonify({"error": "Chapter not found"}), 404
