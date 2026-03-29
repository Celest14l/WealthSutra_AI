# WealthSutra — AI Financial Health & Decision Platform

> An AI-powered financial planning and decision-making platform designed to help Indian users analyze their finances, plan goals, optimize taxes, and achieve financial independence.

WealthSutra combines financial analytics with LLM-based intelligence to deliver personalized, actionable financial strategies.

---

## 🔥 Features

### 📊 Financial Health Score
- Calculates overall financial health score (0–100)
- Category-wise breakdown:
  - Emergency Fund
  - Debt Health
  - Savings Rate
  - Insurance
  - Investments
  - Retirement Readiness
- Personalized improvement suggestions ranked by priority
- Historical score tracking to monitor progress over time

### 📈 FIRE Planner (Financial Independence, Retire Early)
- Projects future wealth using SIP Future Value formula
- Calculates corpus needed using the 25× rule (4% withdrawal rate)
- Determines if user is on track for their target retirement age
- Shows surplus/shortfall with exact rupee amounts
- Scenario analysis: conservative (8%) / moderate (12%) / aggressive (15%)
- Earliest achievable FIRE age calculation

### 🤖 AI Financial Advisor
- Chat-based financial assistant powered by LLM
- Context-aware responses using full user financial profile
- Answers questions like:
  - SIP vs FD — which is better for me?
  - How do I reduce my debt faster?
  - What should I invest in given my risk appetite?
- Persistent conversation history per session
- One-click suggested questions to get started

### 🎯 Smart Goal Planner *(NEW)*
- Plan big financial goals: car, house, education, vacation, etc.
- AI analyzes:
  - Feasibility based on current income and savings
  - Monthly savings required to hit the goal
  - Loan vs savings strategy comparison
  - Risks and personalized recommendations
- Endpoint: `POST /api/goal-plan`

### 💰 Tax Wizard *(NEW)*
- AI-based tax optimization for Indian taxpayers
- Supports:
  - Old vs New tax regime comparison
  - Section 80C, 80D, HRA deduction inputs
- Outputs:
  - Estimated tax liability under both regimes
  - Missed deductions and how to claim them
  - Tax-saving investment strategies (ELSS, NPS, PPF, etc.)
  - Step-by-step action plan before March 31st
- Endpoint: `POST /api/tax-plan`

### 📄 AI Financial Report
- Generates a full personalized financial health report
- Combines Health Score + FIRE data into a narrative
- Includes:
  - Overall financial assessment
  - Top financial problems and opportunities
  - Step-by-step 90-day action plan
- Endpoint: `GET /api/report/<session_id>`

---

## 🧠 Tech Stack

| Layer     | Technology              |
|-----------|-------------------------|
| Frontend  | HTML, CSS, JavaScript   |
| Backend   | Flask (Python)          |
| Database  | SQLite (via SQLAlchemy) |
| AI/LLM    | Groq                    |

---

## 📁 Project Structure

```
wealthsutra/
├── app.py                      ← Flask entry point, registers all blueprints
├── requirements.txt
├── .env.example
├── models/
│   └── models.py               ← SQLAlchemy models (UserProfile, HealthScore, FirePlan, ChatMessage)
├── routes/
│   ├── profile_routes.py       ← /api/profile
│   ├── score_routes.py         ← /api/score
│   ├── fire_routes.py          ← /api/fire
│   ├── chat_routes.py          ← /api/chat, /api/report
│   ├── goal_routes.py          ← /api/goal-plan
│   └── tax_routes.py           ← /api/tax-plan
├── services/
│   ├── score_service.py        ← Money Health Score logic (6 categories)
│   ├── fire_service.py         ← SIP FV formula + corpus calculations
│   └── ai_service.py           ← LLM integration (advisor, report, goal, tax)
├── templates/
│   ├── fire_advisor.html        ← HTML template (if server-side rendering needed)
└── instance/
    └── wealthsutra.db          ← SQLite DB (auto-created on first run)
```

---

## ⚙️ Setup

```bash
# 1. Clone the repo
git clone https://github.com/Celest14/WealthSutra_AI.git
cd wealthsutra

# 2. Create and activate virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # macOS / Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment variables
cp .env.example .env
# Edit .env and fill in:
# GROQ_API_KEY=your_api_key_here
# SECRET_KEY=your_random_secret

# 5. Run the server
python app.py
# API available at http://localhost:5000
```

---

## 🔗 API Endpoints

### 🔑 Session Flow
Every user receives a `session_id` (UUID) on first profile creation.
Pass this `session_id` in every subsequent request.

---

### Profile — `/api/profile`

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/profile` | Create or update user profile |
| `GET` | `/api/profile/<session_id>` | Fetch existing profile |
| `DELETE` | `/api/profile/<session_id>` | Delete profile and all data |

**POST body:**
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
  "session_id": "optional-for-updates"
}
```

---

### Health Score — `/api/score`

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/score` | Calculate and save health score |
| `GET` | `/api/score/history/<session_id>` | Score history (track progress) |
| `POST` | `/api/score/quick` | Stateless score (no session needed) |

---

### FIRE Planner — `/api/fire`

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/fire` | Calculate FIRE projection |
| `GET` | `/api/fire/scenarios/<session_id>` | Conservative / Moderate / Aggressive scenarios |
| `POST` | `/api/fire/quick` | Stateless FIRE calc |

**POST body:**
```json
{
  "session_id": "abc-123",
  "annual_return": 12,
  "inflation": 6,
  "post_expense": 60000,
  "extra_sip": 3000
}
```

---

### AI Advisor — `/api/chat`

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/chat` | Send a message to the advisor |
| `GET` | `/api/chat/history/<session_id>` | Full conversation history |
| `DELETE` | `/api/chat/history/<session_id>` | Clear conversation |

---

### AI Report — `/api/report`

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/report/<session_id>` | Generate full personalized financial report |

---

### Goal Planner — `/api/goal-plan` *(NEW)*

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/goal-plan` | Analyze a financial goal and get AI plan |

**POST body:**
```json
{
  "session_id": "abc-123",
  "goal_name": "Buy a Car",
  "goal_amount": 800000,
  "target_months": 24
}
```

---

### Tax Wizard — `/api/tax-plan` *(NEW)*

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/tax-plan` | Get AI-powered tax optimization plan |

**POST body:**
```json
{
  "session_id": "abc-123",
  "investments_80c": 100000,
  "health_insurance_80d": 25000,
  "hra_exemption": 60000,
  "other_deductions": 0
}
```

---

## 📋 Reference Values

### Insurance
| Value | Meaning |
|-------|---------|
| `none` | No insurance |
| `health` | Health insurance only |
| `term` | Term life only |
| `both` | Term + Health (recommended) |

### Risk Appetite
`conservative` · `moderate` · `aggressive`

---

## 🔌 Connecting the Frontend

Replace direct API calls in `fire_advisor.html` with backend calls:

```javascript
// 1. Save profile → get session_id
const res = await fetch('http://localhost:5000/api/profile', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ ...profileData })
});
const { session_id } = await res.json();
localStorage.setItem('ws_session', session_id);

// 2. Get health score
const score = await fetch('http://localhost:5000/api/score', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ session_id })
}).then(r => r.json());

// 3. Get FIRE plan
const fire = await fetch('http://localhost:5000/api/fire', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ session_id, annual_return: 12, inflation: 6 })
}).then(r => r.json());

// 4. Chat
const chat = await fetch('http://localhost:5000/api/chat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ session_id, message: userText })
}).then(r => r.json());

// 5. Goal planner
const goal = await fetch('http://localhost:5000/api/goal-plan', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ session_id, goal_name: 'Buy a Car', goal_amount: 800000, target_months: 24 })
}).then(r => r.json());

// 6. Tax wizard
const tax = await fetch('http://localhost:5000/api/tax-plan', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ session_id, investments_80c: 100000, health_insurance_80d: 25000 })
}).then(r => r.json());
```

---

## 🚀 Future Scope

- Life Event Advisor (marriage, baby, home purchase planning)
- WhatsApp chatbot integration
- Portfolio analysis (MF X-Ray via CAMS PDF parser)
- Multi-user / couple financial planning
- Risk profiling via ML model
- Tax filing integration

---

## 👨‍💻 Author

Developed by [Celest14](https://github.com/Celest14)
