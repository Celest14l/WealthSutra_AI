# WealthSutra Backend

Flask + SQLite backend for the WealthSutra Indian Financial Advisor platform.

---

## Project Structure

```
wealthsutra/
├── app.py                  ← Flask entry point
├── requirements.txt
├── .env.example
├── models/
│   └── models.py           ← SQLAlchemy models (UserProfile, HealthScore, FirePlan, ChatMessage)
├── services/
│   ├── score_service.py    ← Money Health Score logic
│   ├── fire_service.py     ← FIRE calculator logic
│   └── ai_service.py       ← Claude AI integration
├── routes/
│   ├── profile_routes.py   ← /api/profile
│   ├── score_routes.py     ← /api/score
│   ├── fire_routes.py      ← /api/fire
│   └── chat_routes.py      ← /api/chat, /api/report
└── instance/
    └── wealthsutra.db      ← SQLite DB (auto-created)
```

---

## Setup

```bash
# 1. Clone / enter project
cd wealthsutra

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set environment variables
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY

# 5. Run
python app.py
# Server starts at http://localhost:5000
```

---

## API Reference

### 🔑 Session Flow
Every user gets a `session_id` (UUID) on first profile creation.
Pass this `session_id` in every subsequent request body.

---

### 1. Profile — `/api/profile`

#### `POST /api/profile` — Create or update profile
```json
{
  "age": 28,
  "income": 80000,
  "expenses": 45000,
  "savings": 200000,
  "investments": 10000,
  "debt": 500000,
  "emi": 15000,
  "insurance": "both",
  "risk": "moderate",
  "retire_age": 50,
  "session_id": "optional-existing-uuid"
}
```
**Response:**
```json
{
  "session_id": "abc-123",
  "profile": { ... },
  "message": "Profile saved successfully."
}
```

#### `GET /api/profile/<session_id>` — Fetch profile

#### `DELETE /api/profile/<session_id>` — Delete profile + all data

---

### 2. Money Health Score — `/api/score`

#### `POST /api/score` — Calculate & save score
```json
{ "session_id": "abc-123", "save": true }
```
**Response:**
```json
{
  "score": {
    "total_score": 72.5,
    "badge": "Good",
    "categories": {
      "emergency_fund": { "score": 100, "message": "...", "months_covered": 6.2 },
      "debt_health":    { "score": 65,  "message": "..." },
      "savings_rate":   { "score": 55,  "message": "..." },
      "insurance":      { "score": 60,  "message": "..." },
      "investments":    { "score": 70,  "message": "..." },
      "retirement":     { "score": 80,  "message": "..." }
    },
    "suggestions": [
      { "category": "Savings Rate", "icon": "📈", "score": 55, "action": "Increase SIP by ₹3,000..." }
    ]
  }
}
```

#### `GET /api/score/history/<session_id>` — Score history (track progress)

#### `POST /api/score/quick` — Stateless (no session needed)
Pass raw profile fields directly.

---

### 3. FIRE Planner — `/api/fire`

#### `POST /api/fire` — Calculate FIRE plan
```json
{
  "session_id": "abc-123",
  "annual_return": 12,
  "inflation": 6,
  "post_expense": 60000,
  "extra_sip": 3000,
  "save": true
}
```
**Response:**
```json
{
  "fire": {
    "inputs": { "years_to_retire": 22, "monthly_investment": 13000, ... },
    "projections": {
      "projected_corpus": 45000000,
      "corpus_needed": 38000000,
      "sip_future_value": 43000000,
      "lumpsum_future_value": 2000000
    },
    "analysis": {
      "gap": -7000000,
      "is_on_track": true,
      "progress_pct": 118.4,
      "required_sip": 10500,
      "shortfall_message": "You're on track! Expected surplus of ₹7,000,000.",
      "earliest_fire_age": 48
    }
  }
}
```

#### `GET /api/fire/scenarios/<session_id>` — 3 scenarios: conservative/moderate/aggressive

#### `POST /api/fire/quick` — Stateless FIRE calc

---

### 4. AI Advisor — `/api/chat`

#### `POST /api/chat` — Send a message
```json
{
  "session_id": "abc-123",
  "message": "Should I invest in SIP or FD?",
  "include_history": true
}
```
**Response:**
```json
{
  "reply": "Given your income of ₹80,000 and moderate risk appetite, SIP in equity mutual funds will serve you far better than FDs right now..."
}
```

#### `GET /api/chat/history/<session_id>` — Full conversation history

#### `DELETE /api/chat/history/<session_id>` — Clear chat history

#### `GET /api/report/<session_id>` — Generate full AI financial report

---

## Insurance Values
| Value   | Meaning               |
|---------|-----------------------|
| `none`  | No insurance          |
| `health`| Health only           |
| `term`  | Term life only        |
| `both`  | Term + Health (ideal) |

## Risk Values
`conservative` · `moderate` · `aggressive`

---

## Connecting the Frontend

In your `fire_advisor.html`, replace the direct Anthropic API calls with:

```javascript
// 1. Save profile
const res = await fetch('http://localhost:5000/api/profile', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ ...profileData })
});
const { session_id } = await res.json();
localStorage.setItem('ws_session', session_id);

// 2. Get score
const score = await fetch('http://localhost:5000/api/score', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ session_id })
});

// 3. Chat
const chat = await fetch('http://localhost:5000/api/chat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ session_id, message: userText })
});
```
