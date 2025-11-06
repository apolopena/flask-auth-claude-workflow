"""Token generation and validation utilities for password reset and email verification."""

from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature


def generate_reset_token(email, salt, secret_key):
    """
    Generate a secure time-limited token for password reset.

    Args:
        email: User's email address to encode in token
        salt: Salt value for token generation (prevents token reuse across features)
        secret_key: Application secret key

    Returns:
        str: Secure token string
    """
    serializer = URLSafeTimedSerializer(secret_key)
    return serializer.dumps(email, salt=salt)


def verify_reset_token(token, salt, secret_key, max_age=3600):
    """
    Verify a reset token and return email if valid.

    Args:
        token: Token string to verify
        salt: Salt value used during token generation
        secret_key: Application secret key
        max_age: Maximum token age in seconds (default: 3600 = 1 hour)

    Returns:
        str: User's email address if token is valid
        None: If token is invalid or expired
    """
    serializer = URLSafeTimedSerializer(secret_key)
    try:
        email = serializer.loads(token, salt=salt, max_age=max_age)
        return email
    except (SignatureExpired, BadSignature):
        return None


def generate_verification_token(email, salt, secret_key):
    """
    Generate a secure time-limited token for email verification.

    Args:
        email: User's email address to encode in token
        salt: Salt value for token generation (prevents token reuse across features)
        secret_key: Application secret key

    Returns:
        str: Secure token string
    """
    serializer = URLSafeTimedSerializer(secret_key)
    return serializer.dumps(email, salt=salt)


def verify_verification_token(token, salt, secret_key, max_age=86400):
    """
    Verify an email verification token and return email if valid.

    Args:
        token: Token string to verify
        salt: Salt value used during token generation
        secret_key: Application secret key
        max_age: Maximum token age in seconds (default: 86400 = 24 hours)

    Returns:
        str: User's email address if token is valid
        None: If token is invalid or expired
    """
    serializer = URLSafeTimedSerializer(secret_key)
    try:
        email = serializer.loads(token, salt=salt, max_age=max_age)
        return email
    except (SignatureExpired, BadSignature):
        return None
