"""Database models for the Kudos system."""

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(UserMixin, db.Model):
    """User model for authentication and identification."""
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    department = db.Column(db.String(100), default="")
    join_date = db.Column(db.Date, default=datetime.utcnow)
    is_admin = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    kudos_sent = db.relationship("Kudos", foreign_keys="Kudos.sender_id", backref="sender", lazy="dynamic")
    kudos_received = db.relationship("Kudos", foreign_keys="Kudos.receiver_id", backref="receiver", lazy="dynamic")
    notifications = db.relationship("Notification", backref="user", lazy="dynamic")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def kudos_sent_count(self):
        return self.kudos_sent.count()

    @property
    def kudos_received_count(self):
        return self.kudos_received.count()

    @property
    def unread_notification_count(self):
        return self.notifications.filter_by(is_read=False).count()

    def __repr__(self):
        return f"<User {self.username}>"


class Kudos(db.Model):
    """Kudos model for storing appreciation messages."""
    __tablename__ = "kudos"

    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    receiver_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    message = db.Column(db.Text, nullable=False)
    is_visible = db.Column(db.Boolean, default=True, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    # Moderation fields
    moderated_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    moderated_at = db.Column(db.DateTime, nullable=True)
    moderation_reason = db.Column(db.String(255), nullable=True)

    # Relationships
    moderator = db.relationship("User", foreign_keys=[moderated_by])
    reports = db.relationship("Report", backref="kudos", lazy="dynamic", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Kudos {self.id}: {self.sender_id} -> {self.receiver_id}>"


class Report(db.Model):
    """Report model for flagging inappropriate kudos."""
    __tablename__ = "reports"

    id = db.Column(db.Integer, primary_key=True)
    kudos_id = db.Column(db.Integer, db.ForeignKey("kudos.id"), nullable=False)
    reporter_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    reason = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default="pending")  # pending, reviewed, dismissed
    reviewed_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    reviewed_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    reporter = db.relationship("User", foreign_keys=[reporter_id])
    reviewer = db.relationship("User", foreign_keys=[reviewed_by])

    def __repr__(self):
        return f"<Report {self.id}: kudos={self.kudos_id} status={self.status}>"


class Notification(db.Model):
    """Notification model for in-app notifications."""
    __tablename__ = "notifications"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    kudos_id = db.Column(db.Integer, db.ForeignKey("kudos.id"), nullable=False)
    type = db.Column(db.String(50), nullable=False)  # kudos_received, kudos_reported
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    kudos = db.relationship("Kudos")

    def __repr__(self):
        return f"<Notification {self.id}: user={self.user_id} type={self.type}>"
