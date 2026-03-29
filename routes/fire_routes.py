"""
FIRE Planner Routes — /api/fire
Calculates retirement corpus projections.
"""

from flask import Blueprint, request, jsonify
from models.models import db, UserProfile, FirePlan
from services.fire_service import calculate_fire

fire_bp = Blueprint("fire", __name__)


@fire_bp.route("/fire", methods=["POST"])
def get_fire_plan():
    """
    Calculate FIRE projection for a user.

    Body (JSON):
        session_id (required)
        annual_return (optional, default 12)
        inflation (optional, default 6)
        post_expense (optional, defaults to 80% of current expenses)
        extra_sip (optional, default 0)
        save (optional, default true)
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    session_id = data.get("session_id")
    if not session_id:
        return jsonify({"error": "session_id is required"}), 422

    profile = UserProfile.query.filter_by(session_id=session_id).first()
    if not profile:
        return jsonify({"error": "Profile not found. Create a profile first."}), 404

    # Validate return rate is reasonable
    annual_return = float(data.get("annual_return", 12.0))
    if not (1 <= annual_return <= 30):
        return jsonify({"error": "annual_return must be between 1 and 30"}), 422

    params = {
        "annual_return": annual_return,
        "inflation": float(data.get("inflation", 6.0)),
        "post_expense": float(data.get("post_expense", profile.expenses * 0.8)),
        "extra_sip": float(data.get("extra_sip", 0)),
    }

    result = calculate_fire(profile.to_dict(), params)

    # Persist plan
    if data.get("save", True):
        plan = FirePlan(
            profile_id=profile.id,
            annual_return=params["annual_return"],
            inflation=params["inflation"],
            post_expense=params["post_expense"],
            extra_sip=params["extra_sip"],
            projected_corpus=result["projections"]["projected_corpus"],
            corpus_needed=result["projections"]["corpus_needed"],
            required_sip=result["analysis"]["required_sip"],
            gap=result["analysis"]["gap"],
            progress_pct=result["analysis"]["progress_pct"],
        )
        db.session.add(plan)
        db.session.commit()

    return jsonify({
        "session_id": session_id,
        "fire": result,
    }), 200


@fire_bp.route("/fire/scenarios/<session_id>", methods=["GET"])
def fire_scenarios(session_id):
    """
    Return 3 FIRE scenarios: conservative (8%), moderate (12%), aggressive (15%).
    Useful for showing a range of outcomes.
    """
    profile = UserProfile.query.filter_by(session_id=session_id).first()
    if not profile:
        return jsonify({"error": "Profile not found"}), 404

    base_params = {
        "inflation": 6.0,
        "post_expense": profile.expenses * 0.8,
        "extra_sip": 0,
    }

    scenarios = {}
    for label, rate in [("conservative", 8.0), ("moderate", 12.0), ("aggressive", 15.0)]:
        params = {**base_params, "annual_return": rate}
        scenarios[label] = calculate_fire(profile.to_dict(), params)

    return jsonify({
        "session_id": session_id,
        "scenarios": scenarios,
    }), 200


@fire_bp.route("/fire/quick", methods=["POST"])
def quick_fire():
    """
    Stateless FIRE calculation — no session_id, no DB write.
    Pass full profile + params directly.
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    required = ["age", "income", "expenses", "savings", "investments", "retire_age"]
    missing = [f for f in required if f not in data]
    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 422

    params = {
        "annual_return": float(data.get("annual_return", 12.0)),
        "inflation": float(data.get("inflation", 6.0)),
        "post_expense": float(data.get("post_expense", float(data["expenses"]) * 0.8)),
        "extra_sip": float(data.get("extra_sip", 0)),
    }

    result = calculate_fire(data, params)
    return jsonify({"fire": result}), 200
