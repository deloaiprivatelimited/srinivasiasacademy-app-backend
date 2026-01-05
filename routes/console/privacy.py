"""
Privacy Policy & App Deletion related routes
Register with:
    from privacy import bp as privacy_bp
    app.register_blueprint(privacy_bp, url_prefix="/api")
"""

from flask import Blueprint, request, jsonify
from mongoengine import Document, StringField, BooleanField, DateTimeField
from datetime import datetime

bp = Blueprint("privacy", __name__)

# ----------------------
# Model
# ----------------------
class DeletionRequest(Document):
    email = StringField(required=True)
    user_id = StringField(required=True)
    reason = StringField()
    confirm_delete = BooleanField(required=True)
    status = StringField(default="pending")  # pending | verified | completed | rejected
    created_at = DateTimeField(default=datetime.utcnow)

    meta = {
        "collection": "deletion_requests"
    }


# ----------------------
# User Routes
# ----------------------
@bp.route("/privacy/deletion-request", methods=["POST"])
def create_deletion_request():
    data = request.json

    # Basic validation
    if not data.get("email") or not data.get("userId") or not data.get("confirmDelete"):
        return jsonify({"message": "Missing required fields"}), 400

    deletion = DeletionRequest(
        email=data.get("email"),
        user_id=data.get("userId"),
        reason=data.get("reason"),
        confirm_delete=data.get("confirmDelete"),
    ).save()

    return jsonify({
        "message": "Deletion request submitted successfully",
        "request_id": str(deletion.id),
        "status": deletion.status
    }), 201


# ----------------------
# Admin Routes
# ----------------------
@bp.route("/admin/deletion-requests", methods=["GET"])
def admin_all_deletion_requests():
    requests = DeletionRequest.objects().order_by("-created_at")

    return jsonify([
        {
            "id": str(r.id),
            "email": r.email,
            "user_id": r.user_id,
            "reason": r.reason,
            "status": r.status,
            "created_at": r.created_at
        }
        for r in requests
    ])


@bp.route("/admin/deletion-requests/<req_id>", methods=["PATCH"])
def admin_update_deletion_status(req_id):
    data = request.json

    if "status" not in data:
        return jsonify({"message": "Status is required"}), 400

    DeletionRequest.objects(id=req_id).update(
        status=data["status"]
    )

    return jsonify({"message": "Deletion request status updated"})


@bp.route("/admin/deletion-requests/<req_id>", methods=["GET"])
def admin_deletion_request_details(req_id):
    r = DeletionRequest.objects(id=req_id).first()

    if not r:
        return jsonify({"message": "Deletion request not found"}), 404

    return jsonify({
        "id": str(r.id),
        "email": r.email,
        "user_id": r.user_id,
        "reason": r.reason,
        "confirm_delete": r.confirm_delete,
        "status": r.status,
        "created_at": r.created_at
    })
