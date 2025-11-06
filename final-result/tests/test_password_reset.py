"""Tests for password reset functionality."""

import pytest
from werkzeug.security import check_password_hash
from app import create_app, mail
from models import db, User
from utils.tokens import generate_reset_token, verify_reset_token


@pytest.fixture
def app():
    """Create application for testing."""
    from config import Config

    class TestConfig(Config):
        TESTING = True
        SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
        MAIL_SUPPRESS_SEND = True
        MAIL_DEFAULT_SENDER = "test@example.com"
        # Disable rate limiting in tests
        RATELIMIT_ENABLED = False

    app = create_app(TestConfig)

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


@pytest.fixture
def test_user(app):
    """Create a test user (verified for password reset tests)."""
    from werkzeug.security import generate_password_hash

    user = User(
        email="test@example.com",
        password_hash=generate_password_hash("OldPass123"),
        email_verified=True,
    )
    db.session.add(user)
    db.session.commit()
    return user


def test_forgot_password_with_valid_email(client, test_user, app):
    """Test password reset request with valid email."""
    with mail.record_messages() as outbox:
        response = client.post(
            "/auth/forgot-password",
            json={"email": "test@example.com"},
            content_type="application/json",
        )

        assert response.status_code == 200
        data = response.get_json()
        assert "If an account exists with this email" in data["message"]

        # Verify email was sent
        assert len(outbox) == 1
        assert outbox[0].recipients == ["test@example.com"]
        assert "Password Reset Request" in outbox[0].subject


def test_forgot_password_with_nonexistent_email(client, app):
    """Test password reset request with non-existent email (should still return success)."""
    with mail.record_messages() as outbox:
        response = client.post(
            "/auth/forgot-password",
            json={"email": "nonexistent@example.com"},
            content_type="application/json",
        )

        assert response.status_code == 200
        data = response.get_json()
        assert "If an account exists with this email" in data["message"]

        # Verify no email was sent (user doesn't exist)
        assert len(outbox) == 0


def test_forgot_password_missing_email(client):
    """Test password reset request with missing email field."""
    response = client.post(
        "/auth/forgot-password", json={}, content_type="application/json"
    )

    assert response.status_code == 400
    data = response.get_json()
    assert "Email is required" in data["error"]


def test_forgot_password_non_json_request(client):
    """Test password reset request with non-JSON content type."""
    response = client.post("/auth/forgot-password", data="not json")

    assert response.status_code == 400
    data = response.get_json()
    assert "Content-Type must be application/json" in data["error"]


def test_token_generation_and_verification(app):
    """Test token generation and verification utilities."""
    email = "test@example.com"
    salt = app.config["PASSWORD_RESET_SALT"]
    secret_key = app.config["SECRET_KEY"]

    # Generate token
    token = generate_reset_token(email, salt, secret_key)
    assert token is not None
    assert isinstance(token, str)
    assert len(token) > 0

    # Verify valid token
    verified_email = verify_reset_token(token, salt, secret_key, max_age=3600)
    assert verified_email == email


def test_token_verification_with_invalid_token(app):
    """Test token verification with invalid token."""
    salt = app.config["PASSWORD_RESET_SALT"]
    secret_key = app.config["SECRET_KEY"]

    # Verify invalid token
    verified_email = verify_reset_token("invalid_token", salt, secret_key, max_age=3600)
    assert verified_email is None


def test_token_expiration(app):
    """Test token expiration after max_age."""
    email = "test@example.com"
    salt = app.config["PASSWORD_RESET_SALT"]
    secret_key = app.config["SECRET_KEY"]

    # Generate token
    token = generate_reset_token(email, salt, secret_key)

    # Verify token expires with very short max_age
    # We'll use a negative max_age to simulate expiration
    verified_email = verify_reset_token(token, salt, secret_key, max_age=-1)
    assert verified_email is None


def test_reset_password_with_valid_token(client, test_user, app):
    """Test password reset with valid token."""
    # Generate token
    token = generate_reset_token(
        test_user.email,
        app.config["PASSWORD_RESET_SALT"],
        app.config["SECRET_KEY"],
    )

    # Reset password
    response = client.post(
        "/auth/reset-password",
        json={"token": token, "new_password": "NewPass456"},
        content_type="application/json",
    )

    assert response.status_code == 200
    data = response.get_json()
    assert "Password reset successful" in data["message"]

    # Verify password was updated in database
    with app.app_context():
        user = User.query.filter_by(email=test_user.email).first()
        assert user is not None
        assert check_password_hash(user.password_hash, "NewPass456")


def test_reset_password_with_expired_token(client, test_user, app):
    """Test password reset with expired token."""
    # For integration test, we use an invalid token format which simulates expiration
    # The actual expiration is tested in test_token_expiration() using verify_reset_token
    response = client.post(
        "/auth/reset-password",
        json={"token": "expired_or_invalid_token", "new_password": "NewPass456"},
        content_type="application/json",
    )

    assert response.status_code == 400
    data = response.get_json()
    assert "Invalid or expired reset token" in data["error"]


def test_reset_password_with_missing_fields(client):
    """Test password reset with missing fields."""
    # Missing new_password
    response = client.post(
        "/auth/reset-password",
        json={"token": "some_token"},
        content_type="application/json",
    )

    assert response.status_code == 400
    data = response.get_json()
    assert "Token and new password are required" in data["error"]

    # Missing token
    response = client.post(
        "/auth/reset-password",
        json={"new_password": "NewPass456"},
        content_type="application/json",
    )

    assert response.status_code == 400
    data = response.get_json()
    assert "Token and new password are required" in data["error"]


def test_reset_password_with_weak_password(client, test_user, app):
    """Test password reset with weak password."""
    # Generate valid token
    token = generate_reset_token(
        test_user.email,
        app.config["PASSWORD_RESET_SALT"],
        app.config["SECRET_KEY"],
    )

    # Try to reset with weak password
    response = client.post(
        "/auth/reset-password",
        json={"token": token, "new_password": "weak"},
        content_type="application/json",
    )

    assert response.status_code == 400
    data = response.get_json()
    assert "Password must be at least 8 characters" in data["error"]


def test_reset_password_non_json_request(client):
    """Test password reset with non-JSON content type."""
    response = client.post("/auth/reset-password", data="not json")

    assert response.status_code == 400
    data = response.get_json()
    assert "Content-Type must be application/json" in data["error"]


def test_old_password_no_longer_works_after_reset(client, test_user, app):
    """Test that old password no longer works after password reset."""
    # Verify old password works initially
    response = client.post(
        "/auth/login",
        json={"email": "test@example.com", "password": "OldPass123"},
        content_type="application/json",
    )
    assert response.status_code == 200

    # Generate token and reset password
    token = generate_reset_token(
        test_user.email,
        app.config["PASSWORD_RESET_SALT"],
        app.config["SECRET_KEY"],
    )

    response = client.post(
        "/auth/reset-password",
        json={"token": token, "new_password": "NewPass456"},
        content_type="application/json",
    )
    assert response.status_code == 200

    # Verify old password no longer works
    response = client.post(
        "/auth/login",
        json={"email": "test@example.com", "password": "OldPass123"},
        content_type="application/json",
    )
    assert response.status_code == 401
    data = response.get_json()
    assert "Invalid credentials" in data["error"]


def test_new_password_works_after_reset(client, test_user, app):
    """Test that new password works after password reset."""
    # Generate token and reset password
    token = generate_reset_token(
        test_user.email,
        app.config["PASSWORD_RESET_SALT"],
        app.config["SECRET_KEY"],
    )

    response = client.post(
        "/auth/reset-password",
        json={"token": token, "new_password": "NewPass456"},
        content_type="application/json",
    )
    assert response.status_code == 200

    # Verify new password works
    response = client.post(
        "/auth/login",
        json={"email": "test@example.com", "password": "NewPass456"},
        content_type="application/json",
    )
    assert response.status_code == 200
    data = response.get_json()
    assert "access_token" in data
    assert data["message"] == "Login successful"
