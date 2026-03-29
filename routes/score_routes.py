"""
Health Score Routes — /api/score
Calculates and stores money health scores.
"""

from flask import Blueprint, request, jsonify
from models.models import db, UserProfile, HealthScore
from services.score_service import calculate_health_score

score_bp = Blueprint("score", __name__)


@score_bp.route("/score", methods=["POST"])
def get_score():
    """
    Calculate Money Health Score for a user.

    Body (JSON):
        session_id (required) — links to an existing profile
        save (optional, bool) — whether to persist the score (default: true)
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

    # Calculate score
    result = calculate_health_score(profile.to_dict())

    # Persist score if requested (default: True)
    if data.get("save", True):
        raw = result["scores_raw"]
        score_record = HealthScore(
            profile_id=profile.id,
            total_score=result["total_score"],
            emergency_score=raw["emergency"],
            debt_score=raw["debt"],
            savings_score=raw["savings"],
            insurance_score=raw["insurance"],
            investment_score=raw["investments"],
            retirement_score=raw["retirement"],
        )
        db.session.add(score_record)
        db.session.commit()

    return jsonify({
        "session_id": session_id,
        "score": result,
    }), 200


@score_bp.route("/score/history/<session_id>", methods=["GET"])
def score_history(session_id):
    """
    Return historical scores for a user (to track progress over time).
    """
    profile = UserProfile.query.filter_by(session_id=session_id).first()
    if not profile:
        return jsonify({"error": "Profile not found"}), 404

    scores = (
        HealthScore.query
        .filter_by(profile_id=profile.id)
        .order_by(HealthScore.created_at.desc())
        .limit(20)
        .all()
    )

    return jsonify({
        "session_id": session_id,
        "history": [s.to_dict() for s in scores],
    }), 200


@score_bp.route("/score/quick", methods=["POST"])
def quick_score():
    """
    Stateless score calculation — no session_id required, no DB write.
    Pass raw profile data directly and get a score back.

    Useful for demos or frontend previews.
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    required = ["age", "income", "expenses", "savings", "investments"]
    missing = [f for f in required if f not in data]
    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 422

    result = calculate_health_score(data)
    return jsonify({"score": result}), 200
