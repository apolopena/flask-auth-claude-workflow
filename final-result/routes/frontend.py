"""Frontend routes for rendering HTML pages."""

from flask import Blueprint, render_template, request

frontend_blueprint = Blueprint("frontend", __name__)


@frontend_blueprint.route("/")
def index():
    """Landing page with app overview and call-to-action."""
    return render_template("index.html")


@frontend_blueprint.route("/register")
def register_page():
    """User registration form page."""
    return render_template("register.html")


@frontend_blueprint.route("/login")
def login_page():
    """User login form page."""
    return render_template("login.html")


@frontend_blueprint.route("/dashboard")
def dashboard():
    """
    Protected dashboard showing user information.

    Note: Protection is client-side (JavaScript checks JWT token).
    For truly sensitive data, use server-side JWT validation.
    """
    return render_template("dashboard.html")


@frontend_blueprint.route("/forgot-password")
def forgot_password_page():
    """Password reset request form page."""
    return render_template("forgot_password.html")


@frontend_blueprint.route("/reset-password")
def reset_password_page():
    """
    Password reset completion form page.

    Expects 'token' query parameter from password reset email link.
    """
    token = request.args.get("token", "")
    return render_template("reset_password.html", token=token)


@frontend_blueprint.route("/check-email")
def check_email_page():
    """Post-registration page instructing user to check email."""
    return render_template("check_email.html")


@frontend_blueprint.route("/verify-email")
def verify_email_page():
    """
    Email verification landing page (from email link).

    Expects 'token' query parameter from verification email link.
    """
    token = request.args.get("token", "")
    return render_template("verify_email.html", token=token)
