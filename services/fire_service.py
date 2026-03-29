"""
FIRE (Financial Independence, Retire Early) Calculator Service
Uses SIP future value formula + 25x annual expense rule.
"""

import math


def future_value_sip(monthly_amount: float, annual_return_pct: float, months: int) -> float:
    """
    Future Value of a Systematic Investment Plan (SIP).

    Formula: FV = P × [(1+r)^n - 1] / r × (1+r)
    Where:
        P = monthly investment
        r = monthly return rate
        n = number of months
    """
    if monthly_amount <= 0:
        return 0.0
    if annual_return_pct <= 0:
        return monthly_amount * months

    r = annual_return_pct / 100 / 12  # monthly rate
    fv = monthly_amount * ((math.pow(1 + r, months) - 1) / r) * (1 + r)
    return round(fv, 2)


def future_value_lumpsum(principal: float, annual_return_pct: float, years: float) -> float:
    """Future value of a lump sum investment."""
    if principal <= 0:
        return 0.0
    if annual_return_pct <= 0:
        return principal
    return round(principal * math.pow(1 + annual_return_pct / 100, years), 2)


def required_corpus(monthly_expense_today: float, inflation_pct: float, years: float) -> float:
    """
    Corpus needed at retirement using the 25× rule (4% safe withdrawal rate).
    Adjusts post-retirement expense for inflation first.
    """
    adj_expense = monthly_expense_today * math.pow(1 + inflation_pct / 100, years)
    annual_expense = adj_expense * 12
    corpus = annual_expense * 25  # 25x = 4% withdrawal rate
    return round(corpus, 2)


def required_sip(
    corpus_target: float,
    current_lumpsum: float,
    annual_return_pct: float,
    months: int,
) -> float:
    """
    Monthly SIP required to reach a target corpus given existing savings.

    Inverse of future_value_sip.
    Required P = (corpus_target - lumpsum_fv) × r / [((1+r)^n - 1) × (1+r)]
    """
    if months <= 0:
        return 0.0

    r = annual_return_pct / 100 / 12
    lump_fv = future_value_lumpsum(current_lumpsum, annual_return_pct, months / 12)
    remaining = max(0, corpus_target - lump_fv)

    if r <= 0:
        return round(remaining / months, 2)

    sip = remaining * r / ((math.pow(1 + r, months) - 1) * (1 + r))
    return round(sip, 2)


def years_to_fire(
    current_savings: float,
    monthly_investment: float,
    corpus_target: float,
    annual_return_pct: float,
    max_years: int = 60,
) -> int | None:
    """
    Binary-search for how many years until the projected corpus exceeds target.
    Returns None if not achievable within max_years.
    """
    r = annual_return_pct / 100 / 12
    for y in range(1, max_years + 1):
        n = y * 12
        sip_fv = future_value_sip(monthly_investment, annual_return_pct, n)
        lump_fv = future_value_lumpsum(current_savings, annual_return_pct, y)
        if sip_fv + lump_fv >= corpus_target:
            return y
    return None


# ── Master FIRE calculator ─────────────────────────────────────────────────────

def calculate_fire(profile: dict, params: dict) -> dict:
    """
    Full FIRE plan calculation.

    Args:
        profile: UserProfile dict (age, income, expenses, savings, investments, retire_age)
        params: override dict (annual_return, inflation, post_expense, extra_sip)

    Returns:
        Detailed FIRE projection dict.
    """
    age = int(profile.get("age", 28))
    retire_age = int(profile.get("retire_age", 50))
    savings = float(profile.get("savings", 0))
    base_investments = float(profile.get("investments", 0))
    expenses = float(profile.get("expenses", 0))

    # Params (with defaults)
    annual_return = float(params.get("annual_return", 12.0))
    inflation = float(params.get("inflation", 6.0))
    post_expense = float(params.get("post_expense", expenses * 0.8))
    extra_sip = float(params.get("extra_sip", 0))

    monthly_investment = base_investments + extra_sip
    years = max(1, retire_age - age)
    months = years * 12

    # Projections
    sip_fv = future_value_sip(monthly_investment, annual_return, months)
    lump_fv = future_value_lumpsum(savings, annual_return, years)
    projected_corpus = round(sip_fv + lump_fv, 2)

    # Target
    corpus_needed = required_corpus(post_expense, inflation, years)
    gap = round(corpus_needed - projected_corpus, 2)
    is_on_track = gap <= 0

    req_sip = required_sip(corpus_needed, savings, annual_return, months)
    progress_pct = min(100.0, round((projected_corpus / corpus_needed) * 100, 1))

    # Inflation-adjusted monthly expense at retirement
    adj_post_expense = round(post_expense * math.pow(1 + inflation / 100, years), 2)

    # Alternative: earliest achievable FIRE year
    earliest_fire_years = years_to_fire(savings, monthly_investment, corpus_needed, annual_return)

    # Interpretation message
    if is_on_track:
        shortfall_msg = f"You're on track! Expected surplus of ₹{abs(gap):,.0f}."
    else:
        extra_needed = max(0, req_sip - monthly_investment)
        shortfall_msg = (
            f"Shortfall of ₹{gap:,.0f}. Increase SIP by ₹{extra_needed:,.0f}/month to close the gap."
        )

    return {
        "inputs": {
            "age": age,
            "retire_age": retire_age,
            "years_to_retire": years,
            "monthly_investment": monthly_investment,
            "annual_return_pct": annual_return,
            "inflation_pct": inflation,
            "post_expense": post_expense,
        },
        "projections": {
            "sip_future_value": sip_fv,
            "lumpsum_future_value": lump_fv,
            "projected_corpus": projected_corpus,
            "corpus_needed": corpus_needed,
            "inflation_adjusted_monthly_expense": adj_post_expense,
        },
        "analysis": {
            "gap": gap,
            "is_on_track": is_on_track,
            "progress_pct": progress_pct,
            "required_sip": req_sip,
            "shortfall_message": shortfall_msg,
            "earliest_fire_age": (age + earliest_fire_years) if earliest_fire_years else None,
        },
    }
