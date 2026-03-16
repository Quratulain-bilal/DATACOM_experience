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
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    kudos_sent = db.relationship("Kudos", foreign_keys="Kudos.sender_id", backref="sender", lazy="dynamic")
    kudos_received = db.relationship("Kudos", foreign_keys="Kudos.receiver_id", backref="receiver", lazy="dynamic")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.username}>"


class Kudos(db.Model):
    """Kudos model for storing appreciation messages."""
    __tablename__ = "kudos"

    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_visible = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    # Moderation fields
    moderated_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    moderated_at = db.Column(db.DateTime, nullable=True)
    moderation_reason = db.Column(db.String(255), nullable=True)

    # Relationship for moderator
    moderator = db.relationship("User", foreign_keys=[moderated_by])

    def __repr__(self):
        return f"<Kudos {self.id}: {self.sender_id} -> {self.receiver_id}>"
