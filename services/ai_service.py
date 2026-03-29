"""
AI Financial Advisor Service
Now uses Groq (LLaMA 3) instead of Anthropic
"""

import os
from groq import Groq
from dotenv import load_dotenv
load_dotenv()
print("GROQ KEY:", os.getenv("GROQ_API_KEY"))
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def _build_system_prompt(profile: dict) -> str:
    """Build a powerful, structured financial advisor prompt"""

    income = profile.get("income", 0)
    expenses = profile.get("expenses", 0)
    savings = profile.get("savings", 0)
    investments = profile.get("investments", 0)
    debt = profile.get("debt", 0)
    emi = profile.get("emi", 0)
    insurance = profile.get("insurance", "none")
    risk = profile.get("risk", "moderate")
    retire_age = profile.get("retire_age", 50)
    age = profile.get("age", 28)

    savings_rate = round((investments / income * 100), 1) if income > 0 else 0
    emi_ratio = round((emi / income * 100), 1) if income > 0 else 0

    return f"""
You are WealthSutra AI — an elite Indian financial advisor.

You are NOT a chatbot. You are:
- A strategic wealth coach
- A disciplined financial planner
- A practical decision-maker

-------------------------
📊 USER FINANCIAL PROFILE
-------------------------
Age: {age}
Income: ₹{income:,.0f}/month
Expenses: ₹{expenses:,.0f}/month
Savings: ₹{savings:,.0f}
Investments (SIP): ₹{investments:,.0f}/month ({savings_rate}%)
Debt: ₹{debt:,.0f}
EMI: ₹{emi:,.0f}/month ({emi_ratio}%)
Insurance: {insurance}
Risk: {risk}
Target Retirement Age: {retire_age}

-------------------------
🧠 RESPONSE FRAMEWORK
-------------------------

Always respond in this structure:

1. 📌 Reality Check  
- Briefly analyze their current situation using THEIR numbers

2. ⚠️ Problem / Opportunity  
- Highlight 1–2 key issues or growth opportunities

3. 🚀 Action Plan  
- Give 3 specific steps with exact ₹ amounts

4. 🧭 Smarter Strategy  
- Suggest better alternatives (SIP, ELSS, PPF, NPS, etc.)

5. 🎯 This Week’s Move  
- End with ONE clear action they must take immediately

-------------------------
⚡ RULES
-------------------------
- NEVER give generic advice
- ALWAYS use user's real numbers
- Keep tone sharp, practical, slightly authoritative
- Avoid fluff, no motivational talk
- Keep response under 200 words
- Optimize for Indian finance ecosystem

You are here to improve their financial life — not just answer.
"""


def get_ai_advice(profile: dict, messages: list[dict]) -> str:
    """Generate AI response using Groq"""

    system_prompt = _build_system_prompt(profile)

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",  # ✅ best free fast model
            messages=[
                {"role": "system", "content": system_prompt},
                *messages
            ],
            temperature=0.7,
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"AI Error: {str(e)}"


def build_financial_summary(profile: dict, score_data: dict, fire_data: dict) -> str:
    """Generate structured financial report using Groq"""

    prompt = f"""
Act as a senior Indian financial advisor.

Generate a structured financial report:

1. 🧾 Overall Assessment (2–3 lines)
2. 🔥 Top 3 Financial Problems
3. 📈 Wealth Growth Opportunities
4. 📅 90-Day Action Plan (specific ₹ steps)

-------------------------
DATA
-------------------------
Profile: {profile}

Score: {score_data.get('total_score', 'N/A')} ({score_data.get('badge', '')})

Issues:
{[s['action'] for s in score_data.get('suggestions', [])[:3]]}

FIRE Status:
On Track: {fire_data.get('analysis', {}).get('is_on_track')}
Corpus: ₹{fire_data.get('projections', {}).get('projected_corpus', 0):,.0f}
Needed: ₹{fire_data.get('projections', {}).get('corpus_needed', 0):,.0f}

-------------------------
RULES
-------------------------
- Use exact numbers
- Keep it concise but impactful
- No generic advice
- Make it actionable
"""

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"AI Error: {str(e)}"