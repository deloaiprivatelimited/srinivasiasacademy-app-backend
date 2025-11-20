from flask import Blueprint, request, jsonify
from models.dmq import DMQ  # Assuming you saved the DMQ model in models/dmq.py
from datetime import datetime

dmq_bp = Blueprint('dmq_bp', __name__)

# ------------------- Get All DMQs with Filters -------------------
@dmq_bp.route('/dmq', methods=['GET'])
def get_dmqs():
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    search_query = request.args.get('search', '').lower()
    category_filter = request.args.get('category', '').lower()
    date_filter = request.args.get('date', '')  # Expected format: YYYY-MM-DD

    query = {}

    if search_query:
        query['__raw__'] = {
            "$or": [
                {"questions": {"$regex": search_query, "$options": "i"}},
                {"category": {"$regex": search_query, "$options": "i"}}
            ]
        }

    if category_filter:
        query['category__icontains'] = category_filter

    if date_filter:
        try:
            date_obj = datetime.strptime(date_filter, "%Y-%m-%d")
            query['date__gte'] = date_obj
            query['date__lt'] = date_obj.replace(hour=23, minute=59, second=59)
        except ValueError:
            return jsonify({"error": "Invalid date format, use YYYY-MM-DD"}), 400

    total_dmqs = DMQ.objects(**query).count()
    total_pages = (total_dmqs + per_page - 1) // per_page
    dmqs = DMQ.objects(**query).skip((page - 1) * per_page).limit(per_page)

    return jsonify({
        "total_dmqs": total_dmqs,
        "total_pages": total_pages,
        "current_page": page,
        "dmqs": [dmq.to_json() for dmq in dmqs]
    }), 200


# ------------------- Get DMQ by ID -------------------
@dmq_bp.route('/dmq/<string:dmq_id>', methods=['GET'])
def get_dmq_by_id(dmq_id):
    dmq = DMQ.objects.get_or_404(id=dmq_id)
    return jsonify(dmq.to_json()), 200


# ------------------- Add New DMQ -------------------
@dmq_bp.route('/dmq', methods=['POST'])
def add_dmq():
    data = request.json
    dmq = DMQ(**data)
    dmq.save()
    return jsonify(dmq.to_json()), 201


# ------------------- Update DMQ by ID -------------------
@dmq_bp.route('/dmq/<string:dmq_id>', methods=['PUT'])
def update_dmq(dmq_id):
    data = request.json
    dmq = DMQ.objects.get_or_404(id=dmq_id)
    for key, value in data.items():
        setattr(dmq, key, value)
    dmq.save()
    return jsonify(dmq.to_json()), 200


# ------------------- Delete DMQ by ID -------------------
@dmq_bp.route('/dmq/<string:dmq_id>', methods=['DELETE'])
def delete_dmq(dmq_id):
    DMQ.objects.get_or_404(id=dmq_id).delete()
    return jsonify({"message": "DMQ deleted successfully"}), 200
