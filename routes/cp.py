from mongoengine import (
    Document,
    StringField,
    EmailField,
    DateTimeField,
    URLField
)
from datetime import datetime
ADMIN_SECRET_KEY = "demo21"


class GetEarlyAccessEmails(Document):
    email = EmailField(required=True, unique=True)
    created_at = DateTimeField(default=datetime.utcnow)

    meta = {
        "collection": "get_early_access_emails"
    }


from mongoengine import (
    Document,
    StringField,
    EmailField,
    DateTimeField,
    URLField
)
from datetime import datetime


class InternApplications(Document):
    full_name = StringField(required=True)
    email = EmailField(required=True)
    mobile_whatsapp = StringField(required=True)

    college_name = StringField(required=True)
    dept = StringField(required=True)
    year = StringField(required=True)
    sem = StringField(required=True)

    area_of_interest = StringField(required=True)
    interest_reason = StringField(required=True, max_length=500)
    resume_url = URLField(required=False)

    status = StringField(
        default="pending",
        choices=("pending", "shortlisted", "rejected")
    )

    created_at = DateTimeField(default=datetime.utcnow)

    meta = {
        "collection": "intern_applications"
    }


from flask import Blueprint, request, jsonify

applications_bp = Blueprint("applications", __name__)


@applications_bp.route("/early-access", methods=["POST"])
def early_access():
    data = request.json

    if not data or "email" not in data:
        return jsonify({"error": "Email is required"}), 400

    try:
        entry = GetEarlyAccessEmails(email=data["email"])
        entry.save()
        return jsonify({"message": "Email registered successfully"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 400


@applications_bp.route("/intern-application", methods=["POST"])
def intern_application():
    data = request.json

    required_fields = [
        "full_name",
        "email",
        "mobile_whatsapp",
        "college_name",
        "dept",
        "year",
        "sem",
        "area_of_interest",
        "interest_reason"
    ]

    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"{field} is required"}), 400

    application = InternApplications(
        full_name=data["full_name"],
        email=data["email"],
        mobile_whatsapp=data["mobile_whatsapp"],
        college_name=data["college_name"],
        dept=data["dept"],
        year=data["year"],
        sem=data["sem"],
        area_of_interest=data["area_of_interest"],
        interest_reason=data["interest_reason"],
        resume_url=data.get("resume_url")
    )

    application.save()

    return jsonify({"message": "Application submitted successfully"}), 201




@applications_bp.route("/admin/early-access", methods=["GET"])
def get_all_early_access_emails():
    secret_key = request.args.get("secret_key")

    if secret_key != ADMIN_SECRET_KEY:
        return jsonify({"error": "Unauthorized access"}), 403

    emails = GetEarlyAccessEmails.objects().order_by("-created_at")

    data = [
        {
            "email": entry.email,
            "created_at": entry.created_at
        }
        for entry in emails
    ]

    return jsonify({
        "count": len(data),
        "data": data
    }), 200


@applications_bp.route("/admin/intern-applications", methods=["GET"])
def get_all_intern_applications():
    secret_key = request.args.get("secret_key")

    if secret_key != ADMIN_SECRET_KEY:
        return jsonify({"error": "Unauthorized access"}), 403

    applications = InternApplications.objects().order_by("-created_at")

    data = [
        {
            "_id": str(app.id),
            "full_name": app.full_name,
            "email": app.email,
            "mobile_whatsapp": app.mobile_whatsapp,
            "college_name": app.college_name,
            "dept": app.dept,
            "year": app.year,
            "sem": app.sem,
            "area_of_interest": app.area_of_interest,
            "interest_reason": app.interest_reason,
            "resume_url": app.resume_url,
            "created_at": app.created_at
        }
        for app in applications
    ]

    return jsonify({
        "count": len(data),
        "data": data
    }), 200


from bson import ObjectId


@applications_bp.route("/admin/intern-application/<string:app_id>", methods=["GET"])
def get_intern_application_by_id(app_id):
    secret_key = request.args.get("secret_key")

    if secret_key != ADMIN_SECRET_KEY:
        return jsonify({"error": "Unauthorized access"}), 403

    try:
        application = InternApplications.objects.get(id=ObjectId(app_id))
    except Exception:
        return jsonify({"error": "Application not found"}), 404

    return jsonify({
        "id": str(application.id),
        "full_name": application.full_name,
        "email": application.email,
        "mobile_whatsapp": application.mobile_whatsapp,
        "college_name": application.college_name,
        "dept": application.dept,
        "year": application.year,
        "sem": application.sem,
        "area_of_interest": application.area_of_interest,
        "interest_reason": application.interest_reason,
        "resume_url": application.resume_url,
        "status": application.status,
        "created_at": application.created_at
    }), 200


@applications_bp.route("/admin/intern-application/<string:app_id>/status", methods=["PATCH"])
def update_intern_application_status(app_id):
    secret_key = request.args.get("secret_key")

    if secret_key != ADMIN_SECRET_KEY:
        return jsonify({"error": "Unauthorized access"}), 403

    data = request.json
    new_status = data.get("status")

    if new_status not in ["pending", "shortlisted", "rejected"]:
        return jsonify({
            "error": "Invalid status. Allowed: pending, shortlisted, rejected"
        }), 400

    try:
        application = InternApplications.objects.get(id=ObjectId(app_id))
    except Exception:
        return jsonify({"error": "Application not found"}), 404

    application.status = new_status
    application.save()

    return jsonify({
        "message": "Status updated successfully",
        "application_id": str(application.id),
        "new_status": application.status
    }), 200
