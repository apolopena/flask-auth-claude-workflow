import os
import secrets
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Flask application configuration"""

    # Secret key for session management and CSRF protection
    SECRET_KEY = os.getenv("SECRET_KEY", secrets.token_hex(16))

    # Database configuration
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///users.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Password validation rules
    PASSWORD_MIN_LENGTH = 8

    # JWT configuration
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", secrets.token_hex(32))
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=15)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    JWT_TOKEN_LOCATION = ["headers"]
    JWT_HEADER_NAME = "Authorization"
    JWT_HEADER_TYPE = "Bearer"

    # Email configuration
    MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = int(os.getenv("MAIL_PORT", 587))
    MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "True") == "True"
    MAIL_USE_SSL = os.getenv("MAIL_USE_SSL", "False") == "True"
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER", "noreply@example.com")

    # Password reset configuration
    PASSWORD_RESET_TOKEN_MAX_AGE = 3600  # 1 hour in seconds
    PASSWORD_RESET_SALT = "password-reset-salt"

    # Email verification configuration
    EMAIL_VERIFICATION_TOKEN_MAX_AGE = 86400  # 24 hours in seconds
    EMAIL_VERIFICATION_SALT = "email-verification-salt"
