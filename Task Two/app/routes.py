"""Routes for the Kudos system."""

from datetime import datetime, timedelta
from functools import wraps
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from markupsafe import escape

from .models import db, User, Kudos, Report, Notification
from .forms import RegistrationForm, LoginForm, KudosForm, ReportForm

main = Blueprint("main", __name__)
admin = Blueprint("admin", __name__, url_prefix="/admin")


def admin_required(f):
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            flash("Access denied. Admin privileges required.", "danger")
            return redirect(url_for("main.dashboard"))
        return f(*args, **kwargs)
    return decorated_function


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
        if User.query.filter_by(username=form.username.data).first():
            flash("Username already taken.", "danger")
            return render_template("register.html", form=form)
        if User.query.filter_by(email=form.email.data).first():
            flash("Email already registered.", "danger")
            return render_template("register.html", form=form)
        user = User(username=form.username.data, email=form.email.data, department=form.department.data or "General")
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
    search = request.args.get("q", "", type=str).strip()
    date_filter = request.args.get("filter", "", type=str)
    query = Kudos.query.filter_by(is_visible=True)
    if search:
        query = query.join(User, Kudos.sender_id == User.id).filter(
            db.or_(
                User.username.ilike(f"%{search}%"),
                Kudos.receiver_id.in_(db.session.query(User.id).filter(User.username.ilike(f"%{search}%")))
            )
        )
    now = datetime.utcnow()
    if date_filter == "week":
        query = query.filter(Kudos.created_at >= now - timedelta(weeks=1))
    elif date_filter == "month":
        query = query.filter(Kudos.created_at >= now - timedelta(days=30))
    elif date_filter == "year":
        query = query.filter(Kudos.created_at >= now - timedelta(days=365))
    kudos_feed = query.order_by(Kudos.created_at.desc()).paginate(page=page, per_page=20, error_out=False)
    return render_template("dashboard.html", kudos_feed=kudos_feed, search=search, date_filter=date_filter)


@main.route("/give-kudos", methods=["GET", "POST"])
@login_required
def give_kudos():
    form = KudosForm()
    users = User.query.filter(User.id != current_user.id, User.is_active == True).order_by(User.username).all()
    form.receiver_id.choices = [(u.id, f"{u.username} ({u.department})") for u in users]
    if form.validate_on_submit():
        if form.receiver_id.data == current_user.id:
            flash("You cannot send kudos to yourself.", "danger")
            return render_template("give_kudos.html", form=form)
        five_min_ago = datetime.utcnow() - timedelta(minutes=5)
        duplicate = Kudos.query.filter(Kudos.sender_id == current_user.id, Kudos.receiver_id == form.receiver_id.data, Kudos.message == form.message.data.strip(), Kudos.created_at >= five_min_ago).first()
        if duplicate:
            flash("You already sent this kudos recently. Please wait a few minutes.", "warning")
            return render_template("give_kudos.html", form=form)
        kudos = Kudos(sender_id=current_user.id, receiver_id=form.receiver_id.data, message=escape(form.message.data.strip()))
        db.session.add(kudos)
        db.session.flush()
        db.session.add(Notification(user_id=form.receiver_id.data, kudos_id=kudos.id, type="kudos_received"))
        db.session.commit()
        flash("Kudos sent successfully! 🎉", "success")
        return redirect(url_for("main.dashboard"))
    return render_template("give_kudos.html", form=form)


@main.route("/my-kudos")
@login_required
def my_kudos():
    tab = request.args.get("tab", "received")
    page = request.args.get("page", 1, type=int)
    if tab == "sent":
        kudos_list = current_user.kudos_sent.order_by(Kudos.created_at.desc()).paginate(page=page, per_page=20, error_out=False)
    else:
        kudos_list = current_user.kudos_received.order_by(Kudos.created_at.desc()).paginate(page=page, per_page=20, error_out=False)
    return render_template("my_kudos.html", kudos_list=kudos_list, tab=tab)


@main.route("/profile/<int:user_id>")
@login_required
def profile(user_id):
    user = User.query.get_or_404(user_id)
    recent_received = user.kudos_received.filter_by(is_visible=True).order_by(Kudos.created_at.desc()).limit(5).all()
    recent_sent = user.kudos_sent.filter_by(is_visible=True).order_by(Kudos.created_at.desc()).limit(5).all()
    return render_template("profile.html", profile_user=user, recent_received=recent_received, recent_sent=recent_sent)


@main.route("/report/<int:kudos_id>", methods=["GET", "POST"])
@login_required
def report_kudos(kudos_id):
    kudos = Kudos.query.get_or_404(kudos_id)
    existing = Report.query.filter_by(kudos_id=kudos_id, reporter_id=current_user.id).first()
    if existing:
        flash("You have already reported this kudos.", "warning")
        return redirect(url_for("main.dashboard"))
    form = ReportForm()
    if form.validate_on_submit():
        db.session.add(Report(kudos_id=kudos_id, reporter_id=current_user.id, reason=escape(form.reason.data.strip())))
        db.session.commit()
        flash("Report submitted. An admin will review it shortly.", "info")
        return redirect(url_for("main.dashboard"))
    return render_template("report.html", form=form, kudos=kudos)


@main.route("/notifications")
@login_required
def notifications():
    page = request.args.get("page", 1, type=int)
    notifs = current_user.notifications.order_by(Notification.created_at.desc()).paginate(page=page, per_page=20, error_out=False)
    return render_template("notifications.html", notifications=notifs)


@main.route("/notifications/<int:notif_id>/read", methods=["POST"])
@login_required
def mark_read(notif_id):
    notif = Notification.query.get_or_404(notif_id)
    if notif.user_id == current_user.id:
        notif.is_read = True
        db.session.commit()
    return redirect(url_for("main.notifications"))


@main.route("/notifications/read-all", methods=["POST"])
@login_required
def mark_all_read():
    current_user.notifications.filter_by(is_read=False).update({"is_read": True})
    db.session.commit()
    flash("All notifications marked as read.", "info")
    return redirect(url_for("main.notifications"))


# ─── Admin Routes ──────────────────────────────────────────────

@admin.route("/moderation")
@admin_required
def moderation():
    page = request.args.get("page", 1, type=int)
    all_kudos = Kudos.query.order_by(Kudos.created_at.desc()).paginate(page=page, per_page=50, error_out=False)
    stats = {"total": Kudos.query.count(), "visible": Kudos.query.filter_by(is_visible=True).count(), "hidden": Kudos.query.filter_by(is_visible=False).count(), "pending_reports": Report.query.filter_by(status="pending").count()}
    return render_template("admin/moderation.html", all_kudos=all_kudos, stats=stats)


@admin.route("/hide/<int:kudos_id>", methods=["POST"])
@admin_required
def hide_kudos(kudos_id):
    kudos = Kudos.query.get_or_404(kudos_id)
    kudos.is_visible = not kudos.is_visible
    kudos.moderated_by = current_user.id
    kudos.moderated_at = datetime.utcnow()
    kudos.moderation_reason = request.form.get("reason", "")
    db.session.commit()
    flash(f"Kudos #{kudos_id} has been {'restored' if kudos.is_visible else 'hidden'}.", "info")
    return redirect(url_for("admin.moderation"))


@admin.route("/delete/<int:kudos_id>", methods=["POST"])
@admin_required
def delete_kudos(kudos_id):
    kudos = Kudos.query.get_or_404(kudos_id)
    db.session.delete(kudos)
    db.session.commit()
    flash(f"Kudos #{kudos_id} has been permanently deleted.", "warning")
    return redirect(url_for("admin.moderation"))


@admin.route("/reports")
@admin_required
def admin_reports():
    page = request.args.get("page", 1, type=int)
    reports = Report.query.order_by(Report.created_at.desc()).paginate(page=page, per_page=50, error_out=False)
    return render_template("admin/reports.html", reports=reports)


@admin.route("/reports/<int:report_id>/resolve", methods=["POST"])
@admin_required
def resolve_report(report_id):
    report = Report.query.get_or_404(report_id)
    action = request.form.get("action", "dismiss")
    report.status = "reviewed"
    report.reviewed_by = current_user.id
    report.reviewed_at = datetime.utcnow()
    if action == "hide":
        report.kudos.is_visible = False
        report.kudos.moderated_by = current_user.id
        report.kudos.moderated_at = datetime.utcnow()
        report.kudos.moderation_reason = f"Report #{report.id}: {report.reason}"
        flash(f"Report #{report_id} resolved — kudos hidden.", "info")
    elif action == "delete":
        db.session.delete(report.kudos)
        flash(f"Report #{report_id} resolved — kudos deleted.", "warning")
    else:
        report.status = "dismissed"
        flash(f"Report #{report_id} dismissed.", "info")
    db.session.commit()
    return redirect(url_for("admin.admin_reports"))
