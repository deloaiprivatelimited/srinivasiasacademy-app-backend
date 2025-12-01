# parlour.py
"""
Holds MongoEngine models and Flask Blueprint with all routes
Register the blueprint in your main app with:
    from parlour import bp as parlour_bp
    app.register_blueprint(parlour_bp, url_prefix="/api")
"""
from flask import Blueprint, request, jsonify
from mongoengine import Document, StringField, DateTimeField, FloatField, IntField, ReferenceField
from datetime import datetime

bp = Blueprint("parlour", __name__)

# ----------------------
# Models
# ----------------------
class P1User(Document):
    name = StringField(required=True)
    email = StringField(required=True, unique=True)
    password = StringField(required=True)
    phone = StringField()
    created_at = DateTimeField(default=datetime.utcnow)

class P1Service(Document):
    name = StringField(required=True)
    price = FloatField(required=True)
    duration = IntField()  # minutes

class P1Appointment(Document):
    user = ReferenceField(P1User, required=True)
    service = ReferenceField(P1Service, required=True)
    date_time = DateTimeField(required=True)
    status = StringField(default="scheduled")
    created_at = DateTimeField(default=datetime.utcnow)

# ----------------------
# User routes
# ----------------------
@bp.route("/auth/login", methods=["POST"])
def login():
    data = request.json
    user = P1User.objects(email=data.get("email"), password=data.get("password")).first()
    if not user:
        return jsonify({"message": "Invalid credentials"}), 401
    return jsonify({"message": "Login successful", "user_id": str(user.id)})

@bp.route("/auth/register", methods=["POST"])
def register():
    data = request.json
    user = P1User(**data).save()
    return jsonify({"message": "User created", "user_id": str(user.id)})

@bp.route("/home", methods=["GET"])
def home():
    services = P1Service.objects()
    return jsonify({
        "services": [{"id": str(s.id), "name": s.name, "price": s.price} for s in services]
    })

@bp.route("/users/<user_id>/appointments", methods=["GET"])
def user_appointments(user_id):
    appts = P1Appointment.objects(user=user_id)
    return jsonify([
        {
            "id": str(a.id),
            "service": a.service.name,
            "date_time": a.date_time,
            "status": a.status
        }
        for a in appts
    ])

@bp.route("/appointments/<appt_id>", methods=["PATCH"])
def update_appointment(appt_id):
    P1Appointment.objects(id=appt_id).update(**request.json)
    return jsonify({"message": "Appointment updated"})

@bp.route("/appointments/<appt_id>", methods=["DELETE"])
def delete_appointment(appt_id):
    P1Appointment.objects(id=appt_id).delete()
    return jsonify({"message": "Appointment deleted"})

@bp.route("/services/prices", methods=["GET"])
def price_menu():
    services = P1Service.objects()
    return jsonify([
        {"id": str(s.id), "name": s.name, "price": s.price, "duration": s.duration}
        for s in services
    ])

@bp.route("/users/<user_id>", methods=["GET"])
def get_profile(user_id):
    user = P1User.objects(id=user_id).first()
    if not user:
        return jsonify({"message": "User not found"}), 404
    return jsonify({
        "id": str(user.id),
        "name": user.name,
        "email": user.email,
        "phone": user.phone
    })

@bp.route("/users/<user_id>", methods=["PUT"])
def update_profile(user_id):
    P1User.objects(id=user_id).update(**request.json)
    return jsonify({"message": "Profile updated"})

# ----------------------
# Admin routes
# ----------------------
@bp.route("/admin/auth/login", methods=["POST"])
def admin_login():
    data = request.json
    if data.get("username") == "admin" and data.get("password") == "admin123":
        return jsonify({"message": "Admin login success"})
    return jsonify({"message": "Invalid admin credentials"}), 401

@bp.route("/admin/users", methods=["GET"])
def admin_users():
    users = P1User.objects()
    return jsonify([
        {"id": str(u.id), "name": u.name, "email": u.email, "phone": u.phone}
        for u in users
    ])

@bp.route("/admin/users/<uid>", methods=["GET"])
def admin_user_details(uid):
    u = P1User.objects(id=uid).first()
    if not u:
        return jsonify({"message": "User not found"}), 404
    return jsonify({
        "id": str(u.id),
        "name": u.name,
        "email": u.email,
        "phone": u.phone
    })

@bp.route("/admin/appointments", methods=["GET"])
def admin_all_appointments():
    appts = P1Appointment.objects()
    return jsonify([
        {
            "id": str(a.id),
            "user": a.user.name,
            "service": a.service.name,
            "date_time": a.date_time,
            "status": a.status
        }
        for a in appts
    ])

@bp.route("/admin/appointments/<appt_id>", methods=["GET"])
def admin_appt_details(appt_id):
    a = P1Appointment.objects(id=appt_id).first()
    if not a:
        return jsonify({"message": "Appointment not found"}), 404
    return jsonify({
        "id": str(a.id),
        "user": a.user.name,
        "service": a.service.name,
        "date_time": a.date_time,
        "status": a.status
    })


