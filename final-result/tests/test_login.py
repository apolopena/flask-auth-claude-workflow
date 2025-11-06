import pytest
from app import create_app
from models import db, User
from config import Config
from werkzeug.security import generate_password_hash


class TestConfig(Config):
    """Test configuration with in-memory database"""

    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"


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


@pytest.fixture
def test_user(app):
    """Create a test user in the database (UNVERIFIED by default)"""
    with app.app_context():
        user = User(
            email="test@example.com",
            password_hash=generate_password_hash("SecurePass123"),
            email_verified=False,
        )
        db.session.add(user)
        db.session.commit()
        return user


@pytest.fixture
def verified_user(app):
    """Create a verified test user in the database"""
    with app.app_context():
        user = User(
            email="verified@example.com",
            password_hash=generate_password_hash("VerifiedPass123"),
            email_verified=True,
        )
        db.session.add(user)
        db.session.commit()
        return user


def test_successful_login(client, verified_user):
    """Test successful login with valid credentials"""
    response = client.post(
        "/auth/login",
        json={"email": "verified@example.com", "password": "VerifiedPass123"},
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["message"] == "Login successful"
    assert "access_token" in data
    assert "refresh_token" in data
    assert "user" in data
    assert data["user"]["email"] == "verified@example.com"


def test_login_with_invalid_password(client, verified_user):
    """Test login failure with incorrect password"""
    response = client.post(
        "/auth/login",
        json={"email": "verified@example.com", "password": "WrongPassword"},
    )
    assert response.status_code == 401
    data = response.get_json()
    assert data["error"] == "Invalid credentials"


def test_login_with_nonexistent_email(client):
    """Test login failure with non-existent email"""
    response = client.post(
        "/auth/login",
        json={"email": "nonexistent@example.com", "password": "SecurePass123"},
    )
    assert response.status_code == 401
    data = response.get_json()
    assert data["error"] == "Invalid credentials"


def test_login_missing_email(client):
    """Test login failure with missing email"""
    response = client.post("/auth/login", json={"password": "SecurePass123"})
    assert response.status_code == 400
    data = response.get_json()
    assert data["error"] == "Email and password are required"


def test_login_missing_password(client):
    """Test login failure with missing password"""
    response = client.post("/auth/login", json={"email": "test@example.com"})
    assert response.status_code == 400
    data = response.get_json()
    assert data["error"] == "Email and password are required"


def test_login_non_json_request(client):
    """Test login failure with non-JSON request"""
    response = client.post(
        "/auth/login",
        data="email=test@example.com&password=SecurePass123",
        content_type="application/x-www-form-urlencoded",
    )
    assert response.status_code == 400
    data = response.get_json()
    assert data["error"] == "Content-Type must be application/json"


def test_logout_with_valid_token(client, verified_user):
    """Test successful logout with valid access token"""
    # First, login to get a token
    login_response = client.post(
        "/auth/login",
        json={"email": "verified@example.com", "password": "VerifiedPass123"},
    )
    access_token = login_response.get_json()["access_token"]

    # Now logout with the token
    response = client.post(
        "/auth/logout", headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["message"] == "Logout successful"


def test_logout_without_token(client):
    """Test logout failure without authorization token"""
    response = client.post("/auth/logout")
    assert response.status_code == 401
    data = response.get_json()
    assert data["error"] == "Authorization token is missing"


def test_logout_with_invalid_token(client):
    """Test logout failure with invalid token"""
    response = client.post(
        "/auth/logout", headers={"Authorization": "Bearer invalid_token"}
    )
    assert response.status_code == 401
    data = response.get_json()
    assert data["error"] == "Invalid token"


def test_refresh_token(client, verified_user):
    """Test token refresh with valid refresh token"""
    # First, login to get tokens
    login_response = client.post(
        "/auth/login",
        json={"email": "verified@example.com", "password": "VerifiedPass123"},
    )
    refresh_token = login_response.get_json()["refresh_token"]

    # Now refresh the access token
    response = client.post(
        "/auth/refresh", headers={"Authorization": f"Bearer {refresh_token}"}
    )
    assert response.status_code == 200
    data = response.get_json()
    assert "access_token" in data


def test_refresh_with_access_token_fails(client, verified_user):
    """Test that refresh endpoint rejects access tokens"""
    # Login to get tokens
    login_response = client.post(
        "/auth/login",
        json={"email": "verified@example.com", "password": "VerifiedPass123"},
    )
    access_token = login_response.get_json()["access_token"]

    # Try to refresh with access token (should fail)
    response = client.post(
        "/auth/refresh", headers={"Authorization": f"Bearer {access_token}"}
    )
    # Flask-JWT-Extended returns 401 when wrong token type is used
    assert response.status_code == 401


def test_refresh_without_token(client):
    """Test refresh failure without token"""
    response = client.post("/auth/refresh")
    assert response.status_code == 401
    data = response.get_json()
    assert data["error"] == "Authorization token is missing"


def test_token_can_access_protected_route(client, verified_user):
    """Test that generated token can be used for authentication"""
    # Login to get access token
    login_response = client.post(
        "/auth/login",
        json={"email": "verified@example.com", "password": "VerifiedPass123"},
    )
    assert login_response.status_code == 200
    access_token = login_response.get_json()["access_token"]

    # Verify token is valid by using logout endpoint (which requires JWT)
    response = client.post(
        "/auth/logout", headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 200
