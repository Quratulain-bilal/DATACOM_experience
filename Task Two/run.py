"""Main entry point for the Kudos System application."""

import os
from flask import Flask
from flask_login import LoginManager
from app.models import db, User
from app.routes import main, admin


def create_app():
    """Application factory."""
    app = Flask(__name__, template_folder="app/templates")

    # Configuration
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "kudos-secret-key-change-in-production")
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///kudos.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Initialize extensions
    db.init_app(app)
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "main.login"
    login_manager.login_message_category = "info"

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register blueprints
    app.register_blueprint(main)
    app.register_blueprint(admin)

    # Create database tables
    with app.app_context():
        db.create_all()

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=5000)
