from flask import Blueprint, request, jsonify, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
)
from sqlalchemy.exc import IntegrityError
from email_validator import validate_email, EmailNotValidError
from datetime import datetime
from models import db, User
from config import Config
from utils.tokens import (
    generate_reset_token,
    verify_reset_token,
    generate_verification_token,
    verify_verification_token,
)
from utils.email import send_reset_email, send_verification_email
from app import mail, limiter

auth_blueprint = Blueprint("auth", __name__)


@auth_blueprint.route("/register", methods=["POST"])
def register():
    """
    Register a new user with email and password.

    Request Body:
        {
            "email": "user@example.com",
            "password": "SecurePass123!"
        }

    Returns:
        201: User registered successfully
        400: Invalid email format or weak password
        409: Email already registered
        500: Registration failed (server error)
    """
    # Validate request format
    if not request.is_json:
        return jsonify({"error": "Content-Type must be application/json"}), 400

    data = request.get_json()
    email = data.get("email", "").strip()
    password = data.get("password", "")

    # Validate inputs
    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    # Validate email format
    try:
        validate_email(email, check_deliverability=False)
    except EmailNotValidError:
        return jsonify({"error": "Invalid email format"}), 400

    # Validate password strength
    if len(password) < Config.PASSWORD_MIN_LENGTH:
        return (
            jsonify(
                {
                    "error": f"Password must be at least {Config.PASSWORD_MIN_LENGTH} characters"
                }
            ),
            400,
        )

    # Check for existing user
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({"error": "Email already registered"}), 409

    # Hash password and create user
    password_hash = generate_password_hash(password)
    new_user = User(email=email, password_hash=password_hash)

    # Save to database with error handling
    try:
        db.session.add(new_user)
        db.session.commit()

        # Send verification email AFTER successful commit
        token = generate_verification_token(
            email=new_user.email,
            salt=current_app.config["EMAIL_VERIFICATION_SALT"],
            secret_key=current_app.config["SECRET_KEY"],
        )
        send_verification_email(new_user.email, token, mail)

        return (
            jsonify(
                {
                    "message": "Registration successful! Please check your email to verify your account.",
                    "user_id": new_user.id,
                }
            ),
            201,
        )
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Email already registered"}), 409
    except Exception:
        db.session.rollback()
        return jsonify({"error": "Registration failed"}), 500


@auth_blueprint.route("/login", methods=["POST"])
def login():
    """
    Authenticate user and issue JWT tokens.

    Request Body:
        {
            "email": "user@example.com",
            "password": "SecurePass123!"
        }

    Returns:
        200: Login successful with access and refresh tokens
        400: Missing fields
        401: Invalid credentials
    """
    # Validate request format
    if not request.is_json:
        return jsonify({"error": "Content-Type must be application/json"}), 400

    data = request.get_json()
    email = data.get("email", "").strip()
    password = data.get("password", "")

    # Validate inputs
    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    # Query user by email
    user = User.query.filter_by(email=email).first()

    # Verify user exists and password is correct (constant-time comparison)
    if not user or not check_password_hash(user.password_hash, password):
        # Generic error message - don't reveal which field is wrong
        return jsonify({"error": "Invalid credentials"}), 401

    # Check if email is verified
    if not user.email_verified:
        return (
            jsonify(
                {
                    "error": "Please verify your email address before logging in",
                    "action": "resend_verification",
                    "email": user.email,
                }
            ),
            403,
        )

    # Generate JWT tokens
    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)

    # Return success response with tokens
    return (
        jsonify(
            {
                "message": "Login successful",
                "access_token": access_token,
                "refresh_token": refresh_token,
                "user": {"id": user.id, "email": user.email},
            }
        ),
        200,
    )


@auth_blueprint.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    """
    Logout user (client-side token invalidation).

    Headers:
        Authorization: Bearer <access_token>

    Returns:
        200: Logout successful
    """
    # For JWT, logout is typically client-side (discard token)
    # Optional: Add token to blocklist for server-side revocation
    return jsonify({"message": "Logout successful"}), 200


@auth_blueprint.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    """
    Generate new access token using refresh token.

    Headers:
        Authorization: Bearer <refresh_token>

    Returns:
        200: New access token issued
    """
    # Get identity from refresh token
    current_user_id = get_jwt_identity()

    # Generate new access token
    new_access_token = create_access_token(identity=current_user_id)

    return jsonify({"access_token": new_access_token}), 200


@auth_blueprint.route("/forgot-password", methods=["POST"])
@limiter.limit("3 per hour")
def forgot_password():
    """
    Request password reset and send reset token via email.

    Request Body:
        {
            "email": "user@example.com"
        }

    Returns:
        200: Generic success message (always, for security)
        400: Missing email field
        429: Rate limit exceeded
    """
    # Validate request format
    if not request.is_json:
        return jsonify({"error": "Content-Type must be application/json"}), 400

    data = request.get_json()
    email = data.get("email", "").strip()

    # Validate email field is present
    if not email:
        return jsonify({"error": "Email is required"}), 400

    # Query user by email
    user = User.query.filter_by(email=email).first()

    # If user exists, send reset email
    if user:
        token = generate_reset_token(
            email=user.email,
            salt=current_app.config["PASSWORD_RESET_SALT"],
            secret_key=current_app.config["SECRET_KEY"],
        )
        send_reset_email(user.email, token, mail)

    # Always return success message (don't reveal if email exists)
    return (
        jsonify(
            {
                "message": "If an account exists with this email, you will receive a password reset link"
            }
        ),
        200,
    )


@auth_blueprint.route("/reset-password", methods=["POST"])
def reset_password():
    """
    Reset password using valid token.

    Request Body:
        {
            "token": "reset_token_here",
            "new_password": "NewSecurePass123!"
        }

    Returns:
        200: Password reset successful
        400: Missing fields, weak password, or invalid/expired token
        404: User not found
        500: Password reset failed (server error)
    """
    # Validate request format
    if not request.is_json:
        return jsonify({"error": "Content-Type must be application/json"}), 400

    data = request.get_json()
    token = data.get("token", "")
    new_password = data.get("new_password", "")

    # Validate inputs
    if not token or not new_password:
        return jsonify({"error": "Token and new password are required"}), 400

    if len(new_password) < Config.PASSWORD_MIN_LENGTH:
        return (
            jsonify(
                {
                    "error": f"Password must be at least {Config.PASSWORD_MIN_LENGTH} characters"
                }
            ),
            400,
        )

    # Verify token
    email = verify_reset_token(
        token=token,
        salt=current_app.config["PASSWORD_RESET_SALT"],
        secret_key=current_app.config["SECRET_KEY"],
        max_age=current_app.config["PASSWORD_RESET_TOKEN_MAX_AGE"],
    )

    if email is None:
        return jsonify({"error": "Invalid or expired reset token"}), 400

    # Find user
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    # Update password
    user.password_hash = generate_password_hash(new_password)

    # Save to database
    try:
        db.session.commit()
        return jsonify({"message": "Password reset successful"}), 200
    except Exception:
        db.session.rollback()
        return jsonify({"error": "Password reset failed"}), 500


@auth_blueprint.route("/verify-email", methods=["POST"])
def verify_email():
    """
    Verify email address using token from verification email.

    Request Body:
        {
            "token": "verification_token_here"
        }

    Returns:
        200: Email verified successfully
        400: Missing token or invalid/expired token
        404: User not found
        500: Email verification failed (server error)
    """
    # Validate request format
    if not request.is_json:
        return jsonify({"error": "Content-Type must be application/json"}), 400

    data = request.get_json()
    token = data.get("token", "")

    # Validate token exists
    if not token:
        return jsonify({"error": "Verification token is required"}), 400

    # Verify token
    email = verify_verification_token(
        token=token,
        salt=current_app.config["EMAIL_VERIFICATION_SALT"],
        secret_key=current_app.config["SECRET_KEY"],
        max_age=current_app.config["EMAIL_VERIFICATION_TOKEN_MAX_AGE"],
    )

    if email is None:
        return jsonify({"error": "Invalid or expired verification token"}), 400

    # Find user
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    # Check if already verified (idempotent)
    if user.email_verified:
        return jsonify({"message": "Email already verified"}), 200

    # Update user
    user.email_verified = True
    user.email_verified_at = datetime.utcnow()

    # Save to database
    try:
        db.session.commit()
        return (
            jsonify({"message": "Email verified successfully! You can now login."}),
            200,
        )
    except Exception:
        db.session.rollback()
        return jsonify({"error": "Email verification failed"}), 500


@auth_blueprint.route("/resend-verification", methods=["POST"])
@limiter.limit("3 per hour")
def resend_verification():
    """
    Resend email verification link.

    Request Body:
        {
            "email": "user@example.com"
        }

    Returns:
        200: Generic success message (always, for security)
        400: Missing email field
        429: Rate limit exceeded
    """
    # Validate request format
    if not request.is_json:
        return jsonify({"error": "Content-Type must be application/json"}), 400

    data = request.get_json()
    email = data.get("email", "").strip()

    # Validate email field
    if not email:
        return jsonify({"error": "Email is required"}), 400

    # Query user
    user = User.query.filter_by(email=email).first()

    # Only send if user exists AND is not verified
    if user and not user.email_verified:
        token = generate_verification_token(
            email=user.email,
            salt=current_app.config["EMAIL_VERIFICATION_SALT"],
            secret_key=current_app.config["SECRET_KEY"],
        )
        send_verification_email(user.email, token, mail)

    # Always return success (security: don't reveal email existence or verification status)
    return (
        jsonify(
            {
                "message": "If an unverified account exists with this email, a verification link has been sent."
            }
        ),
        200,
    )
