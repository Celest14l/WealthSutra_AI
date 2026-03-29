from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class UserProfile(db.Model):
    __tablename__ = "user_profiles"

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(64), unique=True, nullable=False)
    age = db.Column(db.Integer, nullable=False)
    income = db.Column(db.Float, nullable=False)
    expenses = db.Column(db.Float, nullable=False)
    savings = db.Column(db.Float, nullable=False)
    investments = db.Column(db.Float, nullable=False)
    debt = db.Column(db.Float, default=0)
    emi = db.Column(db.Float, default=0)
    insurance = db.Column(db.String(20), default="none")
    risk = db.Column(db.String(20), default="moderate")
    retire_age = db.Column(db.Integer, default=50)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    scores = db.relationship("HealthScore", backref="profile", lazy=True, cascade="all, delete-orphan")
    fire_plans = db.relationship("FirePlan", backref="profile", lazy=True, cascade="all, delete-orphan")
    chat_messages = db.relationship("ChatMessage", backref="profile", lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "session_id": self.session_id,
            "age": self.age,
            "income": self.income,
            "expenses": self.expenses,
            "savings": self.savings,
            "investments": self.investments,
            "debt": self.debt,
            "emi": self.emi,
            "insurance": self.insurance,
            "risk": self.risk,
            "retire_age": self.retire_age,
        }


class HealthScore(db.Model):
    __tablename__ = "health_scores"

    id = db.Column(db.Integer, primary_key=True)
    profile_id = db.Column(db.Integer, db.ForeignKey("user_profiles.id"), nullable=False)
    total_score = db.Column(db.Float, nullable=False)
    emergency_score = db.Column(db.Float, nullable=False)
    debt_score = db.Column(db.Float, nullable=False)
    savings_score = db.Column(db.Float, nullable=False)
    insurance_score = db.Column(db.Float, nullable=False)
    investment_score = db.Column(db.Float, nullable=False)
    retirement_score = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "total_score": round(self.total_score, 1),
            "categories": {
                "emergency_fund": round(self.emergency_score, 1),
                "debt_health": round(self.debt_score, 1),
                "savings_rate": round(self.savings_score, 1),
                "insurance": round(self.insurance_score, 1),
                "investments": round(self.investment_score, 1),
                "retirement": round(self.retirement_score, 1),
            },
            "created_at": self.created_at.isoformat(),
        }


class FirePlan(db.Model):
    __tablename__ = "fire_plans"

    id = db.Column(db.Integer, primary_key=True)
    profile_id = db.Column(db.Integer, db.ForeignKey("user_profiles.id"), nullable=False)
    annual_return = db.Column(db.Float, default=12.0)
    inflation = db.Column(db.Float, default=6.0)
    post_expense = db.Column(db.Float, nullable=False)
    extra_sip = db.Column(db.Float, default=0)
    projected_corpus = db.Column(db.Float)
    corpus_needed = db.Column(db.Float)
    required_sip = db.Column(db.Float)
    gap = db.Column(db.Float)
    progress_pct = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "annual_return": self.annual_return,
            "inflation": self.inflation,
            "post_expense": self.post_expense,
            "extra_sip": self.extra_sip,
            "projected_corpus": round(self.projected_corpus, 2),
            "corpus_needed": round(self.corpus_needed, 2),
            "required_sip": round(self.required_sip, 2),
            "gap": round(self.gap, 2),
            "is_on_track": self.gap <= 0,
            "progress_pct": round(self.progress_pct, 1),
            "created_at": self.created_at.isoformat(),
        }


class ChatMessage(db.Model):
    __tablename__ = "chat_messages"

    id = db.Column(db.Integer, primary_key=True)
    profile_id = db.Column(db.Integer, db.ForeignKey("user_profiles.id"), nullable=False)
    session_id = db.Column(db.String(64), nullable=False)
    role = db.Column(db.String(10), nullable=False)  # 'user' or 'assistant'
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "role": self.role,
            "content": self.content,
            "created_at": self.created_at.isoformat(),
        }
