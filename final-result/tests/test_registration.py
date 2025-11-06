import pytest
from app import create_app, mail
from models import db, User
from config import Config


class TestConfig(Config):
    """Test configuration with in-memory database"""

    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    MAIL_SUPPRESS_SEND = True
    MAIL_DEFAULT_SENDER = "test@example.com"
    RATELIMIT_ENABLED = False


@pytest.fixture
def app():
    """Create and configure a test Flask application"""
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Create a test client"""
    return app.test_client()


def test_successful_registration(client, app):
    """Test successful user registration"""
    with mail.record_messages() as outbox:
        response = client.post(
            "/auth/register",
            json={"email": "test@example.com", "password": "SecurePass123"},
        )
        assert response.status_code == 201
        data = response.get_json()
        assert "check your email" in data["message"].lower()
        assert "user_id" in data
        # Verify email was sent
        assert len(outbox) == 1


def test_duplicate_email_registration(client):
    """Test that duplicate email registrations are rejected"""
    # First registration
    client.post(
        "/auth/register",
        json={"email": "test@example.com", "password": "SecurePass123"},
    )
    # Duplicate registration
    response = client.post(
        "/auth/register",
        json={"email": "test@example.com", "password": "AnotherPass123"},
    )
    assert response.status_code == 409
    data = response.get_json()
    assert data["error"] == "Email already registered"


def test_invalid_email_format(client):
    """Test that invalid email format is rejected"""
    response = client.post(
        "/auth/register",
        json={"email": "invalid-email", "password": "SecurePass123"},
    )
    assert response.status_code == 400
    data = response.get_json()
    assert data["error"] == "Invalid email format"


def test_weak_password_rejection(client):
    """Test that weak passwords are rejected"""
    response = client.post(
        "/auth/register", json={"email": "test@example.com", "password": "short"}
    )
    assert response.status_code == 400
    data = response.get_json()
    assert "Password must be at least" in data["error"]


def test_missing_email(client):
    """Test that missing email is rejected"""
    response = client.post("/auth/register", json={"password": "SecurePass123"})
    assert response.status_code == 400
    data = response.get_json()
    assert data["error"] == "Email and password are required"


def test_missing_password(client):
    """Test that missing password is rejected"""
    response = client.post("/auth/register", json={"email": "test@example.com"})
    assert response.status_code == 400
    data = response.get_json()
    assert data["error"] == "Email and password are required"


def test_non_json_request(client):
    """Test that non-JSON requests are rejected"""
    response = client.post(
        "/auth/register",
        data="email=test@example.com&password=SecurePass123",
        content_type="application/x-www-form-urlencoded",
    )
    assert response.status_code == 400
    data = response.get_json()
    assert data["error"] == "Content-Type must be application/json"


def test_password_is_hashed(client, app):
    """Test that passwords are hashed before storage"""
    password = "SecurePass123"
    client.post(
        "/auth/register", json={"email": "test@example.com", "password": password}
    )

    with app.app_context():
        user = User.query.filter_by(email="test@example.com").first()
        assert user is not None
        assert user.password_hash != password
        # Check that password is hashed (Werkzeug uses scrypt or pbkdf2)
        assert user.password_hash.startswith(("scrypt:", "pbkdf2:"))
