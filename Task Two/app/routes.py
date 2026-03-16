"""Routes for the Kudos system."""

from datetime import datetime, timedelta
from functools import wraps
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from markupsafe import escape

from .models import db, User, Kudos
from .forms import RegistrationForm, LoginForm, KudosForm

main = Blueprint("main", __name__)
admin = Blueprint("admin", __name__, url_prefix="/admin")


def admin_required(f):
    """Decorator to restrict access to admin users only."""
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            flash("Access denied. Admin privileges required.", "danger")
            return redirect(url_for("main.dashboard"))
        return f(*args, **kwargs)
    return decorated_function


# ─── Main Routes ───────────────────────────────────────────────

@main.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))
    return redirect(url_for("main.login"))


@main.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    form = RegistrationForm()
    if form.validate_on_submit():
        # Check if username or email already exists
        if User.query.filter_by(username=form.username.data).first():
            flash("Username already taken.", "danger")
            return render_template("register.html", form=form)
        if User.query.filter_by(email=form.email.data).first():
            flash("Email already registered.", "danger")
            return render_template("register.html", form=form)

        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("Registration successful! Please log in.", "success")
        return redirect(url_for("main.login"))

    return render_template("register.html", form=form)


@main.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash(f"Welcome back, {user.username}!", "success")
            return redirect(url_for("main.dashboard"))
        else:
            flash("Invalid username or password.", "danger")

    return render_template("login.html", form=form)


@main.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("main.login"))


@main.route("/dashboard")
@login_required
def dashboard():
    page = request.args.get("page", 1, type=int)
    kudos_feed = (
        Kudos.query
        .filter_by(is_visible=True)
        .order_by(Kudos.created_at.desc())
        .paginate(page=page, per_page=20, error_out=False)
    )
    return render_template("dashboard.html", kudos_feed=kudos_feed)


@main.route("/give-kudos", methods=["GET", "POST"])
@login_required
def give_kudos():
    form = KudosForm()
    # Populate dropdown with all users except current user
    users = User.query.filter(User.id != current_user.id).order_by(User.username).all()
    form.receiver_id.choices = [(u.id, u.username) for u in users]

    if form.validate_on_submit():
        # Prevent self-kudos
        if form.receiver_id.data == current_user.id:
            flash("You cannot send kudos to yourself.", "danger")
            return render_template("give_kudos.html", form=form)

        # Check for duplicate submission within 5 minutes
        five_min_ago = datetime.utcnow() - timedelta(minutes=5)
        duplicate = Kudos.query.filter(
            Kudos.sender_id == current_user.id,
            Kudos.receiver_id == form.receiver_id.data,
            Kudos.message == form.message.data.strip(),
            Kudos.created_at >= five_min_ago,
        ).first()

        if duplicate:
            flash("You already sent this kudos recently. Please wait a few minutes.", "warning")
            return render_template("give_kudos.html", form=form)

        kudos = Kudos(
            sender_id=current_user.id,
            receiver_id=form.receiver_id.data,
            message=escape(form.message.data.strip()),
        )
        db.session.add(kudos)
        db.session.commit()
        flash("Kudos sent successfully! 🎉", "success")
        return redirect(url_for("main.dashboard"))

    return render_template("give_kudos.html", form=form)


# ─── Admin Routes ──────────────────────────────────────────────

@admin.route("/moderation")
@admin_required
def moderation():
    page = request.args.get("page", 1, type=int)
    all_kudos = (
        Kudos.query
        .order_by(Kudos.created_at.desc())
        .paginate(page=page, per_page=50, error_out=False)
    )
    return render_template("admin/moderation.html", all_kudos=all_kudos)


@admin.route("/hide/<int:kudos_id>", methods=["POST"])
@admin_required
def hide_kudos(kudos_id):
    kudos = Kudos.query.get_or_404(kudos_id)
    kudos.is_visible = not kudos.is_visible
    kudos.moderated_by = current_user.id
    kudos.moderated_at = datetime.utcnow()
    kudos.moderation_reason = request.form.get("reason", "")
    db.session.commit()

    action = "restored" if kudos.is_visible else "hidden"
    flash(f"Kudos #{kudos_id} has been {action}.", "info")
    return redirect(url_for("admin.moderation"))


@admin.route("/delete/<int:kudos_id>", methods=["POST"])
@admin_required
def delete_kudos(kudos_id):
    kudos = Kudos.query.get_or_404(kudos_id)
    db.session.delete(kudos)
    db.session.commit()
    flash(f"Kudos #{kudos_id} has been permanently deleted.", "warning")
    return redirect(url_for("admin.moderation"))
