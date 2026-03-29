"""
AI Advisor Routes — /api/chat
Handles multi-turn financial conversations powered by Claude.
"""

from flask import Blueprint, request, jsonify
from models.models import db, UserProfile, ChatMessage
from services.ai_service import get_ai_advice
from services.score_service import calculate_health_score
from services.fire_service import calculate_fire
from services.ai_service import build_financial_summary
from services.ai_service import client

chat_bp = Blueprint("chat", __name__)

MAX_HISTORY = 20  # max messages sent to LLM to keep context manageable

@chat_bp.route("/goal-plan", methods=["POST"])
def goal_plan():
    try:
        data = request.get_json()

        session_id = data.get("session_id")
        goal = data.get("goal", {})

        name = goal.get("name")
        cost = goal.get("cost")
        years = goal.get("years")

        if not session_id or not name or not cost or not years:
            return jsonify({"error": "Missing goal data"}), 400

        profile = UserProfile.query.filter_by(session_id=session_id).first()
        if not profile:
            return jsonify({"error": "Profile not found"}), 404

        from services.ai_service import client

        prompt = f"""
User: {profile.to_dict()}
Goal: {name}, ₹{cost}, {years} years

Give:
- Feasibility
- Monthly plan
- Savings vs loan
- Risks
"""

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}]
        )

        reply = response.choices[0].message.content

        return jsonify({"plan": reply})

    except Exception as e:
        print("ERROR:", str(e))
        return jsonify({"error": str(e)}), 500
    
@chat_bp.route("/chat", methods=["POST"])
def chat():
    """
    Send a message to the AI financial advisor.

    Body (JSON):
        session_id (required)
        message (required) — user's question
        include_history (optional, default true) — send conversation history to LLM
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    session_id = data.get("session_id")
    user_message = data.get("message", "").strip()

    if not session_id:
        return jsonify({"error": "session_id is required"}), 422
    if not user_message:
        return jsonify({"error": "message cannot be empty"}), 422
    if len(user_message) > 2000:
        return jsonify({"error": "message too long (max 2000 chars)"}), 422

    profile = UserProfile.query.filter_by(session_id=session_id).first()
    if not profile:
        return jsonify({"error": "Profile not found. Create a profile first."}), 404

    # Save user message to DB
    user_msg_record = ChatMessage(
        profile_id=profile.id,
        session_id=session_id,
        role="user",
        content=user_message,
    )
    db.session.add(user_msg_record)
    db.session.flush()  # get id without full commit

    # Build message history for LLM
    if data.get("include_history", True):
        past = (
            ChatMessage.query
            .filter_by(profile_id=profile.id)
            .order_by(ChatMessage.created_at.desc())
            .limit(MAX_HISTORY)
            .all()
        )
        past.reverse()
        messages = [{"role": m.role, "content": m.content} for m in past]
    else:
        messages = [{"role": "user", "content": user_message}]

    # Call AI
    try:
        reply = get_ai_advice(profile.to_dict(), messages)
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"AI service error: {str(e)}"}), 503

    # Save assistant reply
    bot_msg_record = ChatMessage(
        profile_id=profile.id,
        session_id=session_id,
        role="assistant",
        content=reply,
    )
    db.session.add(bot_msg_record)
    db.session.commit()

    return jsonify({
        "session_id": session_id,
        "reply": reply,
    }), 200

@chat_bp.route("/life-plan", methods=["POST"])
def life_plan():
    data = request.get_json()
    session_id = data.get("session_id")
    event = data.get("event")

    profile = UserProfile.query.filter_by(session_id=session_id).first()

    prompt = f"""
User: {profile.to_dict()}

Life Event: {event}

Give:
- Financial impact
- Preparation needed
- Monthly cost
- Mistakes to avoid
- Action plan
"""

    from services.ai_service import client

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}]
    )

    return jsonify({"plan": response.choices[0].message.content})

@chat_bp.route("/chat/history/<session_id>", methods=["GET"])
def chat_history(session_id):
    """Return full conversation history for a session."""
    profile = UserProfile.query.filter_by(session_id=session_id).first()
    if not profile:
        return jsonify({"error": "Profile not found"}), 404

    limit = min(int(request.args.get("limit", 50)), 200)
    messages = (
        ChatMessage.query
        .filter_by(profile_id=profile.id)
        .order_by(ChatMessage.created_at.asc())
        .limit(limit)
        .all()
    )

    return jsonify({
        "session_id": session_id,
        "messages": [m.to_dict() for m in messages],
    }), 200

@chat_bp.route("/tax-plan", methods=["POST"])
def tax_plan():
    try:
        data = request.get_json()

        session_id = data.get("session_id")
        tax = data.get("tax", {})

        profile = UserProfile.query.filter_by(session_id=session_id).first()
        if not profile:
            return jsonify({"error": "Profile not found"}), 404

        prompt = f"""
You are a tax expert for India.

User Profile:
{profile.to_dict()}

Tax Details:
- Income: ₹{tax.get('income')}
- Regime: {tax.get('regime')}
- 80C: ₹{tax.get('c80')}
- 80D: ₹{tax.get('d80')}
- HRA: ₹{tax.get('hra')}

Give:

1. 🧾 Estimated Tax
2. ⚖️ Old vs New Regime Comparison
3. 💡 Missed Deductions
4. 📈 Tax Saving Strategy
5. 📅 Action Plan

Be practical and specific.
"""

        from services.ai_service import client

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}]
        )

        return jsonify({"plan": response.choices[0].message.content})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@chat_bp.route("/chat/history/<session_id>", methods=["DELETE"])
def clear_history(session_id):
    """Clear conversation history for a session."""
    profile = UserProfile.query.filter_by(session_id=session_id).first()
    if not profile:
        return jsonify({"error": "Profile not found"}), 404

    ChatMessage.query.filter_by(profile_id=profile.id).delete()
    db.session.commit()
    return jsonify({"message": "Conversation history cleared."}), 200


@chat_bp.route("/report/<session_id>", methods=["GET"])
def generate_report(session_id):
    """
    Generate a full AI-written financial health report.
    Combines score + FIRE data into a personalised narrative.
    """
    profile = UserProfile.query.filter_by(session_id=session_id).first()
    if not profile:
        return jsonify({"error": "Profile not found"}), 404

    profile_dict = profile.to_dict()
    score_data = calculate_health_score(profile_dict)
    fire_data = calculate_fire(
        profile_dict,
        {"annual_return": 12, "inflation": 6, "post_expense": profile.expenses * 0.8, "extra_sip": 0},
    )

    try:
        report = build_financial_summary(profile_dict, score_data, fire_data)
    except Exception as e:
        return jsonify({"error": f"Report generation failed: {str(e)}"}), 503

    return jsonify({
        "session_id": session_id,
        "report": report,
        "score_summary": {
            "total": score_data["total_score"],
            "badge": score_data["badge"],
        },
        "fire_summary": {
            "is_on_track": fire_data["analysis"]["is_on_track"],
            "progress_pct": fire_data["analysis"]["progress_pct"],
        },
    }), 200
