from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.conf import settings
from .tokens import email_verification_token, password_reset_token


def send_verification_email(user, request):
    token = email_verification_token.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    domain = request.get_host()
    link = f"http://{domain}/api/v1/auth/verify-email/{uid}/{token}/"

    send_mail(
        subject='Verify your ScholarLink account',
        message=f'Click the link to verify your email: {link}',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        html_message=f'''
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: auto; padding: 20px;">
            <h2 style="color: #1a9e8f;">Welcome to ScholarLink!</h2>
            <p>Hi {user.first_name},</p>
            <p>Please verify your email address to complete your registration.</p>
            <a href="{link}" style="
                background: #1a9e8f;
                color: white;
                padding: 12px 24px;
                text-decoration: none;
                border-radius: 6px;
                display: inline-block;
                margin: 20px 0;
            ">Verify Email →</a>
            <p style="color: #666;">If you didn't create an account, please ignore this email.</p>
            <hr>
            <p style="color: #999; font-size: 12px;">ScholarLink - Connecting Scholars Worldwide</p>
        </div>
        ''',
        fail_silently=False,
    )


def send_password_reset_email(user, request):
    token = password_reset_token.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    domain = request.get_host()
    link = f"http://{domain}/api/v1/auth/reset-password/{uid}/{token}/"

    send_mail(
        subject='Reset your ScholarLink password',
        message=f'Click the link to reset your password: {link}',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        html_message=f'''
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: auto; padding: 20px;">
            <h2 style="color: #1a9e8f;">Reset Your Password</h2>
            <p>Hi {user.first_name},</p>
            <p>We received a request to reset your password.</p>
            <a href="{link}" style="
                background: #1a9e8f;
                color: white;
                padding: 12px 24px;
                text-decoration: none;
                border-radius: 6px;
                display: inline-block;
                margin: 20px 0;
            ">Reset Password →</a>
            <p style="color: #666;">This link expires in 1 hour. If you didn't request this, please ignore this email.</p>
            <hr>
            <p style="color: #999; font-size: 12px;">ScholarLink - Connecting Scholars Worldwide</p>
        </div>
        ''',
        fail_silently=False,
    )