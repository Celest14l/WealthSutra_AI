"""
Profile Routes — /api/profile
Handles creating and fetching user profiles (keyed by session_id).
"""

import uuid
from flask import Blueprint, request, jsonify
from models.models import db, UserProfile

profile_bp = Blueprint("profile", __name__)

REQUIRED_FIELDS = ["age", "income", "expenses", "savings", "investments"]


@profile_bp.route("/profile", methods=["POST"])
def create_or_update_profile():
    """
    Create or update a user profile.
    If session_id is provided in the body, update the existing profile.
    Otherwise, create a new one and return a fresh session_id.

    Body (JSON):
        age, income, expenses, savings, investments,
        debt, emi, insurance, risk, retire_age
        session_id (optional)
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    # Validate required fields
    missing = [f for f in REQUIRED_FIELDS if f not in data or data[f] is None]
    if missing:
        return jsonify({"error": f"Missing required fields: {', '.join(missing)}"}), 422

    # Basic range validation
    age = int(data["age"])
    if not (10 <= age <= 100):
        return jsonify({"error": "Age must be between 10 and 100"}), 422

    retire_age = int(data.get("retire_age", 50))
    if retire_age <= age:
        return jsonify({"error": "Retirement age must be greater than current age"}), 422

    session_id = data.get("session_id") or str(uuid.uuid4())
    profile = UserProfile.query.filter_by(session_id=session_id).first()

    if profile:
        # Update existing
        profile.age = age
        profile.income = float(data["income"])
        profile.expenses = float(data["expenses"])
        profile.savings = float(data["savings"])
        profile.investments = float(data["investments"])
        profile.debt = float(data.get("debt", 0))
        profile.emi = float(data.get("emi", 0))
        profile.insurance = data.get("insurance", "none")
        profile.risk = data.get("risk", "moderate")
        profile.retire_age = retire_age
    else:
        profile = UserProfile(
            session_id=session_id,
            age=age,
            income=float(data["income"]),
            expenses=float(data["expenses"]),
            savings=float(data["savings"]),
            investments=float(data["investments"]),
            debt=float(data.get("debt", 0)),
            emi=float(data.get("emi", 0)),
            insurance=data.get("insurance", "none"),
            risk=data.get("risk", "moderate"),
            retire_age=retire_age,
        )
        db.session.add(profile)

    db.session.commit()

    return jsonify({
        "session_id": session_id,
        "profile": profile.to_dict(),
        "message": "Profile saved successfully.",
    }), 200


@profile_bp.route("/profile/<session_id>", methods=["GET"])
def get_profile(session_id):
    """Fetch a profile by session_id."""
    profile = UserProfile.query.filter_by(session_id=session_id).first()
    if not profile:
        return jsonify({"error": "Profile not found"}), 404
    return jsonify({"profile": profile.to_dict()}), 200


@profile_bp.route("/profile/<session_id>", methods=["DELETE"])
def delete_profile(session_id):
    """Delete a profile and all related data."""
    profile = UserProfile.query.filter_by(session_id=session_id).first()
    if not profile:
        return jsonify({"error": "Profile not found"}), 404
    db.session.delete(profile)
    db.session.commit()
    return jsonify({"message": "Profile deleted."}), 200
