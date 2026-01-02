from mongoengine import (
    Document,
    StringField,
    EmailField,
    DateTimeField,
    URLField
)
from datetime import datetime


class GetEarlyAccessEmails(Document):
    email = EmailField(required=True, unique=True)
    created_at = DateTimeField(default=datetime.utcnow)

    meta = {
        "collection": "get_early_access_emails"
    }


class InternApplications(Document):
    full_name = StringField(required=True)
    email = EmailField(required=True)
    mobile_whatsapp = StringField(required=True)

    college_name = StringField(required=True)
    dept = StringField(required=True)
    year = StringField(required=True)
    sem = StringField(required=True)

    area_of_interest = StringField(required=True)  
    # you can store as comma-separated values if selecting up to 2

    interest_reason = StringField(required=True, max_length=500)
    resume_url = URLField(required=False)

    created_at = DateTimeField(default=datetime.utcnow)

    meta = {
        "collection": "intern_applications"
    }


from flask import Blueprint, request, jsonify
from models import GetEarlyAccessEmails, InternApplications

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
