from app import db
from flask_login import UserMixin
from datetime import datetime

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    alert_preference = db.relationship('AlertPreference', backref='user', uselist=False)
    diary_entries = db.relationship('DiaryEntry', backref='author', lazy=True)
    comments = db.relationship('Comment', backref='author', lazy=True)
    incidents_reported = db.relationship('Incident', backref='reporter', lazy=True)

    def set_password(self, password):
        from werkzeug.security import generate_password_hash
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        from werkzeug.security import check_password_hash
        return check_password_hash(self.password_hash, password)

class AlertPreference(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email_alerts = db.Column(db.Boolean, default=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class DiaryEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    photo_filename = db.Column(db.String(150))
    public = db.Column(db.Boolean, default=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    comments = db.relationship('Comment', backref='diary_entry', lazy=True)

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    diary_entry_id = db.Column(db.Integer, db.ForeignKey('diary_entry.id'), nullable=False)

class Incident(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    incident_type = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(200), nullable=False)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    photo_filename = db.Column(db.String(150))
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default='Pending')  # Pending, Approved, Rejected
    risk_category = db.Column(db.String(50))  # e.g., crime, flood, health
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
