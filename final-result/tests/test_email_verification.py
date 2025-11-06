"""Tests for email verification functionality."""

import pytest
from app import create_app, mail
from models import db, User
from config import Config


@pytest.fixture
def app():
    """Create application for testing."""

    class TestConfig(Config):
        TESTING = True
        SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
        MAIL_SUPPRESS_SEND = True
        MAIL_DEFAULT_SENDER = "test@example.com"
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
    """Create a test user (UNVERIFIED by default)."""
    from werkzeug.security import generate_password_hash

    user = User(
        email="test@example.com",
        password_hash=generate_password_hash("TestPassword123"),
        email_verified=False,
    )
    db.session.add(user)
    db.session.commit()
    return user


def test_registration_sends_verification_email(client, app):
    """Test that registration sends verification email instead of allowing immediate login."""
    with mail.record_messages() as outbox:
        response = client.post(
            "/auth/register",
            json={"email": "newuser@example.com", "password": "Password123"},
            content_type="application/json",
        )

        assert response.status_code == 201
        data = response.get_json()
        assert "check your email" in data["message"].lower()

        # Verify email was sent
        assert len(outbox) == 1
        assert outbox[0].recipients == ["newuser@example.com"]
        assert "Verify Your Email" in outbox[0].subject


def test_unverified_user_cannot_login(client, test_user):
    """Test that unverified users cannot login."""
    response = client.post(
        "/auth/login",
        json={"email": "test@example.com", "password": "TestPassword123"},
        content_type="application/json",
    )

    assert response.status_code == 403
    data = response.get_json()
    assert "verify your email" in data["error"].lower()
    assert data["action"] == "resend_verification"


def test_email_verification_with_valid_token(client, test_user, app):
    """Test email verification with valid token sets email_verified=True."""
    from utils.tokens import generate_verification_token

    token = generate_verification_token(
        test_user.email,
        app.config["EMAIL_VERIFICATION_SALT"],
        app.config["SECRET_KEY"],
    )

    # Verify email
    response = client.post(
        "/auth/verify-email",
        json={"token": token},
        content_type="application/json",
    )

    assert response.status_code == 200
    data = response.get_json()
    assert "verified successfully" in data["message"].lower()

    # Check database
    with app.app_context():
        user = User.query.filter_by(email=test_user.email).first()
        assert user.email_verified is True
        assert user.email_verified_at is not None


def test_verified_user_can_login(client, app):
    """Test that verified users CAN login."""
    from werkzeug.security import generate_password_hash

    # Create a verified user
    with app.app_context():
        user = User(
            email="verified_login@example.com",
            password_hash=generate_password_hash("TestPassword123"),
            email_verified=True,
        )
        db.session.add(user)
        db.session.commit()

    # Login should succeed
    response = client.post(
        "/auth/login",
        json={"email": "verified_login@example.com", "password": "TestPassword123"},
        content_type="application/json",
    )

    assert response.status_code == 200
    data = response.get_json()
    assert "access_token" in data


def test_verification_token_expiration(client, test_user, app):
    """Test that expired verification tokens are rejected."""
    from utils.tokens import generate_verification_token, verify_verification_token

    token = generate_verification_token(
        test_user.email,
        app.config["EMAIL_VERIFICATION_SALT"],
        app.config["SECRET_KEY"],
    )

    # Verify with very short max_age (simulating expiration)
    email = verify_verification_token(
        token,
        app.config["EMAIL_VERIFICATION_SALT"],
        app.config["SECRET_KEY"],
        max_age=-1,  # Already expired
    )

    assert email is None


def test_resend_verification_email(client, test_user, app):
    """Test resending verification email."""
    with mail.record_messages() as outbox:
        response = client.post(
            "/auth/resend-verification",
            json={"email": "test@example.com"},
            content_type="application/json",
        )

        assert response.status_code == 200
        data = response.get_json()
        assert "verification link has been sent" in data["message"].lower()

        # Verify email was sent
        assert len(outbox) == 1


def test_resend_verification_for_already_verified_user(client, app):
    """Test resending verification for already verified user doesn't send email."""
    from werkzeug.security import generate_password_hash

    # Create an already verified user
    with app.app_context():
        user = User(
            email="already_verified@example.com",
            password_hash=generate_password_hash("TestPassword123"),
            email_verified=True,
        )
        db.session.add(user)
        db.session.commit()

    with mail.record_messages() as outbox:
        response = client.post(
            "/auth/resend-verification",
            json={"email": "already_verified@example.com"},
            content_type="application/json",
        )

        # Still returns success (security: don't reveal verification status)
        assert response.status_code == 200

        # But no email sent (user already verified)
        assert len(outbox) == 0


def test_verification_is_idempotent(client, test_user, app):
    """Test clicking verification link multiple times works (idempotent)."""
    from utils.tokens import generate_verification_token

    token = generate_verification_token(
        test_user.email,
        app.config["EMAIL_VERIFICATION_SALT"],
        app.config["SECRET_KEY"],
    )

    # Verify first time
    response1 = client.post(
        "/auth/verify-email", json={"token": token}, content_type="application/json"
    )
    assert response1.status_code == 200

    # Verify second time (same token)
    response2 = client.post(
        "/auth/verify-email", json={"token": token}, content_type="application/json"
    )
    assert response2.status_code == 200
    data = response2.get_json()
    assert "already verified" in data["message"].lower()
