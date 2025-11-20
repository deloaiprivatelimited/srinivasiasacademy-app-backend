from flask import Blueprint, request, jsonify
from models.tests import Test ,QuestionDetail # Assuming your Test model is in models/test.py
from mongoengine import DoesNotExist
from models.question import Question

test_blueprint = Blueprint('test', __name__)

# Route to get all tests
@test_blueprint.route('/tests', methods=['GET'])
def get_all_tests():
#    tests = Test.objects.order_by('name')
    tests = Test.objects.order_by('order_index')

    return jsonify([test.to_json_admin() for test in tests]), 200

@test_blueprint.route("tests/reorder", methods=["POST"])
def reorder_tests():
    """
    Expects JSON like:
    {
      "new_order": ["test_id_1", "test_id_2", "test_id_3", ...]
    }
    """
    data = request.get_json()
    new_order = data.get("new_order", [])

    # For each test ID in the new_order list,
    # set test.order_index = position in the list
    for index, test_id in enumerate(new_order):
        print(test_id)
        print(index)
        test = Test.objects(id=test_id).first()
        if test:
            test.order_index = index
            test.save()

    return jsonify({"message": "Test order updated successfully"}), 200
# Route to create a new test
@test_blueprint.route('/tests', methods=['POST'])
def create_test():
    data = request.json
# Find the MINIMUM order_index among existing tests
    existing_tests = Test.objects()
    if existing_tests:
        min_order_index = min(t.order_index for t in existing_tests)
    else:
        # If no tests exist yet, start at 0 (or any number).
        min_order_index = 0
    new_test = Test(
        name=data['name'],
        start_date=data['start_date'],
        start_time=data['start_time'],
        duration=data['duration'],
        # questions=data['questions']  # Assuming this is a list
        end_date=data['end_date'],
        end_time=data['end_time'],
        order_index=min_order_index - 1,

    )
    new_test.save()
    return jsonify(new_test.to_json()), 201


# Route to update a test by ID
@test_blueprint.route('/tests/<string:test_id>', methods=['PUT'])
def update_test(test_id):
    data = request.json
    try:
        test = Test.objects.get(id=test_id)
        test.update(**data)  # Update fields with the provided data
        test.reload()  # Reload the updated test from the database
        return jsonify(test.to_json()), 200
    except DoesNotExist:
        return jsonify({'error': 'Test not found'}), 404

# Route to delete a test by ID
@test_blueprint.route('/tests/<string:test_id>', methods=['DELETE'])
def delete_test(test_id):
    try:
        test = Test.objects.get(id=test_id)
        res = test.delete_test()
        return jsonify({'message': 'Test deleted successfully'}), 200
    except DoesNotExist:
        return jsonify({'error': 'Test not found'}), 404


# Route to add a question to a test
@test_blueprint.route('/tests/<string:test_id>/add_question', methods=['POST'])
def add_question_to_test(test_id):
    data = request.json

    # Check for question ID
    question_id = data.get('question_id')

    try:
        test = Test.objects.get(id=test_id)  # Retrieve the test by ID

        if question_id:
            # If question ID is provided, check if the question exists
            question = Question.objects.get(id=question_id)
            question_detail = QuestionDetail(
                    id=str(question.id),
                    question=question.question,
                    question_image=question.question_image,
                    option_a=question.option_a,
                    option_b=question.option_b,
                    option_c=question.option_c,
                    option_d=question.option_d,
                    correct_option=question.correct_option,
                    crt_ans_score=question.crt_ans_score,
                    wrong_ans_score=question.wrong_ans_score
                )
            if not any(q.id == question_detail.id for q in test.questions):
                test.questions.append(question_detail)  # Add question detail to the test's questions list
            else:
                return jsonify({'error': 'Question already exists in this test'}), 400

        else:
            # If question ID is not provided, create a new question using the existing add_question logic
            question = Question(**data)  # Unpack the data to create a Question object
            
            question.save() 
             # Save the new question
            question_detail = QuestionDetail(
                    id=str(question.id),
                    question=question.question,
                    question_image=question.question_image,
                    option_a=question.option_a,
                    option_b=question.option_b,
                    option_c=question.option_c,
                    option_d=question.option_d,
                    correct_option=question.correct_option,
                    crt_ans_score=question.crt_ans_score,
                    wrong_ans_score=question.wrong_ans_score
                )
            test.questions.append(question_detail)  # Add new question ID to the test's questions list

        test.save()  # Save the updated test
        return jsonify({"message": "Question added successfully", "test": test.to_json()}), 200

    except DoesNotExist:
        return jsonify({'error': 'Test not found'}), 404
    except Exception as e:
        print(e)
        return jsonify({'error': str(e)}), 500


@test_blueprint.route('/tests/<string:test_id>', methods=['GET'])
def get_test_by_id(test_id):
    try:
        test = Test.objects.get(id=test_id)
        return jsonify(test.to_json()), 200
    except DoesNotExist:
        return jsonify({'error': 'Test not found'}), 404



@test_blueprint.route('/tests/<string:test_id>/<string:student_id>/secure', methods=['GET'])
def get_test_by_id_secure(test_id,student_id):
    try:
        test = Test.objects.get(id=test_id)
        return jsonify(test.to_json_secure(student_id)), 200
    except DoesNotExist:
        return jsonify({'error': 'Test not found'}), 404


@test_blueprint.route('/test/<test_id>/remove_question/<question_id>', methods=['DELETE'])
def remove_question(test_id, question_id):
    try:
        # Call the method to remove the question
        success = Test.remove_question(test_id, question_id)
        return jsonify({"message": "Question removed successfully"}), 200 if success else 400
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
@test_blueprint.route('/tests/<string:test_id>/questions/<string:question_id>', methods=['PUT'])
def update_embedded_question(test_id, question_id):
    data = request.json
    
    try:
        test = Test.objects.get(id=test_id)  # Retrieve the test by ID
        
        # Find the embedded question by its ID
        question_to_update = None
        for question in test.questions:
            if str(question.id) == question_id:
                question_to_update = question
                break
        
        if question_to_update:
            # Update the values of the found question
            for key, value in data.items():
                setattr(question_to_update, key, value)
            test.save()  # Save the updated test with the modified question
            return jsonify(test.to_json()), 200
        else:
            return jsonify({'error': 'Question not found in the test'}), 404
            
    except DoesNotExist:
        return jsonify({'error': 'Test not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@test_blueprint.route('/enroll_student', methods=['POST'])
def enroll_student():
    try:
        # Extract test_id and student_id from the request JSON
        data = request.get_json()
        test_id = data.get('test_id')
        student_id = data.get('student_id')
        
        if not test_id or not student_id:
            return jsonify({"message": "Missing test_id or student_id", "success": False, "data": {}}), 400
        
        # Enroll the student in the test
        enrolled = Test.enroll_student(test_id, student_id)
        
        if enrolled:
            return jsonify({"message": "Student enrolled successfully", "success": True, "data": {}}), 200
        else:
            return jsonify({"message": "Student is already enrolled", "success": False, "data": {}}), 409
    except ValueError as e:
        return jsonify({"message": str(e), "success": False, "data": {}}), 404
    except Exception as e:
        return jsonify({"message": "An error occurred", "success": False, "data": {}}), 500


@test_blueprint.route('/unenroll_student', methods=['POST'])
def unenroll_student():
    try:
        # Extract test_id and student_id from the request JSON
        data = request.get_json()
        test_id = data.get('test_id')
        student_id = data.get('student_id')
        
        if not test_id or not student_id:
            return jsonify({"message": "Missing test_id or student_id", "success": False, "data": {}}), 400
        
        # Unenroll the student from the test
        unenrolled = Test.unenroll_student(test_id, student_id)
        
        if unenrolled:
            return jsonify({"message": "Student unenrolled successfully", "success": True, "data": {}}), 200
        else:
            return jsonify({"message": "Student is not enrolled in this test", "success": False, "data": {}}), 409
    except ValueError as e:
        return jsonify({"message": str(e), "success": False, "data": {}}), 404
    except Exception as e:
        return jsonify({"message": "An error occurred", "success": False, "data": {}}), 500


@test_blueprint.route('/tests/<test_id>/submit', methods=['POST'])
def submit_test_results(test_id):
    data = request.get_json()
    
    # Expecting data in the form: {'student_id': '...', 'responses': [{'question_id': '...', 'answer': '...'}]}
    student_id = data.get('student_id')
    responses = data.get('responses')
    print(responses)
    
    if not student_id or not responses:
        return jsonify({"message": "Student ID and responses are required", "success": False}), 400
    
    try:
        Test.record_result(test_id, student_id, responses)
        return jsonify({"message": "Results recorded successfully", "success": True}), 200
    except ValueError as e:
        print(e)
        return jsonify({"message": str(e), "success": False}), 400



@test_blueprint.route('/tests/<test_id>/result', methods=['GET'])
def get_test_result(test_id):
    student_id = request.args.get('student_id')

    # Find the test by ID
    test = Test.objects(id=test_id).first()
    
    if not test:
        return jsonify({'error': 'Test not found'}), 404

    # Find the student's result
    result = next((res for res in test.results if res.student_id == student_id), None)
    
    if not result:
        return jsonify({'error': 'No results found for this student'}), 404

    # Convert result to JSON
    result_json = test.to_json_secure_with_q(student_id)

    return jsonify(result_json), 200




@test_blueprint.route('/start_test/<test_id>/<student_id>', methods=['POST'])
def start_test(test_id, student_id):
    from models.student import Student
    from models.tests import Result
    test = Test.objects(id=test_id).first()
    student = Student.objects(id=student_id).first()
    
    if not test or not student:
        return jsonify({"error": "Test or Student not found"}), 404
    
    # Initialize student result
    result = Result(student_id=str(student_id), responses=[], score=0, status=-1)
    test.results.append(result)
    test.save()
    
    return jsonify({"message": "Test started successfully", "result": result.to_json()}), 200
