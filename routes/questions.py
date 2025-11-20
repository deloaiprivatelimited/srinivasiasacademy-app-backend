from flask import Blueprint, request, jsonify
from models.question import Question

question_bp = Blueprint('question_bp', __name__)

@question_bp.route('/questions', methods=['GET'])
def get_questions():
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    search_query = request.args.get('search', '').lower()

    query = {}
    if search_query:
        query['question__icontains'] = search_query

    total_questions = Question.objects(**query).count()
    total_pages = (total_questions + per_page - 1) // per_page
    questions = Question.objects(**query).skip((page - 1) * per_page).limit(per_page)

    return jsonify({
        "total_questions": total_questions,
        "total_pages": total_pages,
        "current_page": page,
        "questions": [question.to_json() for question in questions]
    }), 200

@question_bp.route('/questions', methods=['POST'])
def add_question():
    data = request.json
    print(data)
    question = Question(**data)
    question.save()
    return jsonify(question.to_json()), 201
    # return ''

@question_bp.route('/questions/<string:question_id>', methods=['PUT'])
def update_question(question_id):
    data = request.json
    question = Question.objects.get(id=question_id)
    for key, value in data.items():
        setattr(question, key, value)
    question.save()
    return jsonify(question.to_json()), 200

@question_bp.route('/questions/<string:question_id>', methods=['DELETE'])
def delete_question(question_id):
    Question.objects.get(id=question_id).delete()
    return jsonify({"message": "Question deleted successfully"}), 200

@question_bp.route('/questions/type/<string:question_type>', methods=['GET'])
def get_questions_by_type(question_type):
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    search_query = request.args.get('search', '').lower()

    # Adjust the query based on question_type
    query = {}
    if question_type != "All":
        query['question_type'] = question_type

    if search_query:
        query['question__icontains'] = search_query

    total_questions = Question.objects(**query).count()
    total_pages = (total_questions + per_page - 1) // per_page
    questions = Question.objects(**query).skip((page - 1) * per_page).limit(per_page)

    return jsonify({
        "total_questions": total_questions,
        "total_pages": total_pages,
        "current_page": page,
        "questions": [question.to_json() for question in questions]
    }), 200
