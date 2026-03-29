"""
Money Health Score Service
Calculates a 0–100 score across 6 financial health dimensions.
"""


# ── Individual category scorers ────────────────────────────────────────────────

def emergency_fund_score(savings: float, monthly_expense: float) -> dict:
    """Score based on how many months of expenses are covered by savings."""
    if monthly_expense <= 0:
        return {"score": 0, "message": "Monthly expenses cannot be zero.", "months_covered": 0}

    months = savings / monthly_expense

    if months >= 6:
        score = 100
        message = f"You have {months:.1f} months covered — excellent emergency fund!"
    elif months >= 3:
        score = 70
        shortfall = (6 - months) * monthly_expense
        message = f"{months:.1f} months covered. Save ₹{shortfall:,.0f} more to reach the 6-month target."
    elif months >= 1:
        score = 40
        shortfall = (3 - months) * monthly_expense
        message = f"Only {months:.1f} months covered. Build at least 3 months (₹{shortfall:,.0f}) as an urgent priority."
    else:
        score = 10
        message = "Critical: Less than 1 month of expenses saved. Start an emergency fund immediately."

    return {"score": score, "message": message, "months_covered": round(months, 1)}


def debt_health_score(emi: float, income: float) -> dict:
    """Score based on EMI-to-income ratio. Ideal: < 30%."""
    if income <= 0:
        return {"score": 0, "message": "Income cannot be zero.", "emi_ratio_pct": 0}

    if emi == 0:
        return {"score": 100, "message": "Debt-free! Excellent financial health.", "emi_ratio_pct": 0}

    ratio = emi / income
    ratio_pct = round(ratio * 100, 1)

    if ratio <= 0.20:
        score = 90
        message = f"EMI is {ratio_pct}% of income — well within healthy limits (< 20%)."
    elif ratio <= 0.30:
        score = 65
        message = f"EMI is {ratio_pct}% of income — manageable, but keep an eye on this."
    elif ratio <= 0.40:
        score = 40
        excess = (ratio - 0.30) * income
        message = f"EMI is {ratio_pct}% of income — above the 30% threshold. Reduce by ₹{excess:,.0f}/month."
    else:
        score = 15
        message = f"EMI is {ratio_pct}% of income — dangerously high. Prioritise debt repayment immediately."

    return {"score": score, "message": message, "emi_ratio_pct": ratio_pct}


def savings_rate_score(investments: float, income: float) -> dict:
    """Score based on monthly savings/investment as % of income. Ideal: >= 20%."""
    if income <= 0:
        return {"score": 0, "message": "Income cannot be zero.", "savings_rate_pct": 0}

    rate = investments / income
    rate_pct = round(rate * 100, 1)
    gap_amount = max(0, 0.20 * income - investments)

    if rate >= 0.30:
        score = 100
        message = f"Saving {rate_pct}% of income — you're in the top tier of savers!"
    elif rate >= 0.20:
        score = 80
        message = f"Saving {rate_pct}% of income — right on target. Keep it up."
    elif rate >= 0.10:
        score = 55
        message = f"Saving {rate_pct}% of income. Increase SIP by ₹{gap_amount:,.0f}/month to reach the ideal 20%."
    elif rate > 0:
        score = 30
        message = f"Saving only {rate_pct}% of income. A ₹{gap_amount:,.0f}/month SIP increase is strongly recommended."
    else:
        score = 5
        message = "Not investing anything. Start a SIP — even ₹500/month makes a difference."

    return {"score": score, "message": message, "savings_rate_pct": rate_pct}


def insurance_score(insurance_type: str) -> dict:
    """Score based on insurance coverage type."""
    mapping = {
        "both": {
            "score": 100,
            "message": "Complete coverage with term + health insurance. Your family is well protected.",
        },
        "term": {
            "score": 60,
            "message": "Term plan protects your family's future. Add health insurance to cover medical bills.",
        },
        "health": {
            "score": 50,
            "message": "Health insurance covers medical costs. Add a term plan to protect your family's income.",
        },
        "none": {
            "score": 10,
            "message": "No insurance is a critical risk. Get ₹1 Cr term + ₹5L health cover as soon as possible.",
        },
    }
    return mapping.get(insurance_type, mapping["none"])


def investment_diversification_score(investments: float, income: float, risk: str) -> dict:
    """Score based on investment rate + risk alignment."""
    if income <= 0:
        return {"score": 0, "message": "Income cannot be zero."}

    rate = investments / income
    base = 40

    if rate >= 0.20:
        base = 85
    elif rate >= 0.15:
        base = 70
    elif rate >= 0.10:
        base = 55

    # Risk appetite bonus
    bonus = {"conservative": 0, "moderate": 5, "aggressive": 10}.get(risk, 0)
    score = min(100, base + bonus)

    if rate >= 0.20:
        message = f"Strong investor at {rate*100:.0f}% of income. Ensure diversification across equity, debt, and gold."
    elif rate >= 0.10:
        message = f"Investing {rate*100:.0f}% of income. Aim for at least 15% and diversify across asset classes."
    else:
        needed = round(0.15 * income)
        message = f"Investing only {rate*100:.0f}% of income. Start a ₹{needed:,.0f}/month SIP for long-term wealth creation."

    return {"score": score, "message": message}


def retirement_readiness_score(age: int, retire_age: int, investments: float, income: float) -> dict:
    """Score based on years to retire + savings rate."""
    years_left = retire_age - age
    if years_left <= 0:
        return {"score": 50, "message": "You have reached or passed your target retirement age.", "years_left": 0}

    rate = investments / max(income, 1)
    # Weighted: more years = more time to recover, higher rate = higher score
    time_factor = min(1.0, years_left / 30)
    rate_factor = min(1.0, rate / 0.25)
    score = round((time_factor * 40 + rate_factor * 60))

    if score >= 80:
        message = f"{years_left} years to retirement with strong savings — great trajectory!"
    elif score >= 50:
        message = f"{years_left} years to FIRE. Increase SIP gradually every year to stay on track."
    else:
        message = f"Only {years_left} years to retirement. Aggressive saving + equity exposure is needed now."

    return {"score": score, "message": message, "years_left": years_left}


# ── Master scorer ──────────────────────────────────────────────────────────────

def calculate_health_score(profile: dict) -> dict:
    """
    Master function that returns full health score report.

    Args:
        profile: dict with keys: age, income, expenses, savings, investments,
                 debt, emi, insurance, risk, retire_age

    Returns:
        Full score report with total, per-category scores, badge, and suggestions.
    """
    age = int(profile.get("age", 28))
    income = float(profile.get("income", 0))
    expenses = float(profile.get("expenses", 0))
    savings = float(profile.get("savings", 0))
    investments = float(profile.get("investments", 0))
    emi = float(profile.get("emi", 0))
    insurance = profile.get("insurance", "none")
    risk = profile.get("risk", "moderate")
    retire_age = int(profile.get("retire_age", 50))

    # Calculate individual categories
    emergency = emergency_fund_score(savings, expenses)
    debt = debt_health_score(emi, income)
    savings_r = savings_rate_score(investments, income)
    insur = insurance_score(insurance)
    invest = investment_diversification_score(investments, income, risk)
    retirement = retirement_readiness_score(age, retire_age, investments, income)

    categories = {
        "emergency_fund": {**emergency, "icon": "🛡️", "label": "Emergency Fund"},
        "debt_health": {**debt, "icon": "💳", "label": "Debt Health"},
        "savings_rate": {**savings_r, "icon": "📈", "label": "Savings Rate"},
        "insurance": {**insur, "icon": "☂️", "label": "Insurance"},
        "investments": {**invest, "icon": "🏦", "label": "Investments"},
        "retirement": {**retirement, "icon": "🎯", "label": "Retirement Readiness"},
    }

    scores = [v["score"] for v in categories.values()]
    total = round(sum(scores) / len(scores), 1)

    # Badge
    if total >= 80:
        badge = "Excellent"
        badge_color = "green"
    elif total >= 60:
        badge = "Good"
        badge_color = "amber"
    elif total >= 40:
        badge = "Needs Work"
        badge_color = "amber"
    else:
        badge = "Critical"
        badge_color = "red"

    # Top suggestions (lowest-scoring categories first)
    sorted_cats = sorted(categories.items(), key=lambda x: x[1]["score"])
    suggestions = [
        {
            "category": v["label"],
            "icon": v["icon"],
            "score": v["score"],
            "action": v["message"],
        }
        for _, v in sorted_cats[:4]
        if v["score"] < 80
    ]

    return {
        "total_score": total,
        "badge": badge,
        "badge_color": badge_color,
        "categories": categories,
        "suggestions": suggestions,
        "scores_raw": {
            "emergency": emergency["score"],
            "debt": debt["score"],
            "savings": savings_r["score"],
            "insurance": insur["score"],
            "investments": invest["score"],
            "retirement": retirement["score"],
        },
    }
