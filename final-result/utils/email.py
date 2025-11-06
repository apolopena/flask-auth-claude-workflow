"""Email sending utilities for password reset and email verification."""

from flask_mail import Message


def send_reset_email(user_email, reset_token, mail_instance):
    """
    Send password reset email with token link.

    Args:
        user_email: Recipient email address
        reset_token: Password reset token
        mail_instance: Flask-Mail instance

    Returns:
        bool: True if email sent successfully, False otherwise
    """
    try:
        # Link to frontend password reset page
        reset_url = f"http://localhost:5000/reset-password?token={reset_token}"

        msg = Message(
            subject="Password Reset Request",
            recipients=[user_email],
        )

        msg.body = f"""Hello,

You have requested to reset your password. Use the following token to reset your password:

{reset_token}

Or visit this URL:
{reset_url}

This link will expire in 1 hour.

If you did not request this, please ignore this email.

Best regards,
Your Application Team
"""

        mail_instance.send(msg)
        return True
    except Exception as e:
        # Log error but don't expose to user
        print(f"Error sending email: {e}")
        return False


def send_verification_email(user_email, verification_token, mail_instance):
    """
    Send email verification email with token link.

    Args:
        user_email: Recipient email address
        verification_token: Email verification token
        mail_instance: Flask-Mail instance

    Returns:
        bool: True if email sent successfully, False otherwise
    """
    try:
        # Link to frontend email verification page
        verify_url = f"http://localhost:5000/verify-email?token={verification_token}"

        msg = Message(
            subject="Verify Your Email Address",
            recipients=[user_email],
        )

        msg.body = f"""Hello,

Thank you for registering! Please verify your email address by clicking the link below:

{verify_url}

This link will expire in 24 hours.

If you did not create an account, please ignore this email.

Best regards,
Your Application Team
"""

        mail_instance.send(msg)
        return True
    except Exception as e:
        # Log error but don't expose to user
        print(f"Error sending email: {e}")
        return False
