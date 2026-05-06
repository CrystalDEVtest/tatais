"""
Notification utilities for the service system.

Supports:
  - In-app notifications (always active)
  - Email notifications (via SMTP in settings)
  - SMS notifications (via SMSAero API or console fallback)

Setup:
  1. Email: Configure EMAIL_* settings in settings.py
     - For Yandex: smtp.yandex.ru, port 587, TLS
     - For Gmail: smtp.gmail.com, port 587, TLS
     - Use "App passwords" for Google accounts

  2. SMS: Set SMS_PROVIDER to 'smsaero' and fill SMSAERO_* settings
     - Register at smsaero.ru
     - Get API key
     - Register sender name
"""

import json
import logging
import urllib.request
import urllib.parse
import urllib.error

from django.conf import settings
from django.core.mail import send_mail
from django.utils.html import strip_tags

from .models import Notification, EmailLog, SMSLog

logger = logging.getLogger(__name__)


# ===== IN-APP NOTIFICATIONS =====

def create_notification(ticket, notification_type, message):
    """
    Create in-app notification for relevant users.
    Also triggers email and SMS delivery.
    """
    recipients = _get_recipients(ticket)

    for user in recipients:
        Notification.objects.create(
            user=user,
            ticket=ticket,
            notification_type=notification_type,
            title=f'Заявка #{ticket.ticket_number}',
            message=message,
        )

    # Send email
    try:
        send_ticket_email(ticket, notification_type, message)
    except Exception as e:
        logger.error(f'Email send failed: {e}')

    # Send SMS
    try:
        phone = None
        if ticket.customer:
            phone = ticket.customer.phone
        if not phone:
            phone = getattr(ticket, 'guest_phone', '')

        if phone:
            send_sms(phone, f'TatAIS: {message[:70]}')
    except Exception as e:
        logger.error(f'SMS send failed: {e}')


def _get_recipients(ticket):
    """Determine notification recipients based on ticket data."""
    recipients = []

    if ticket.customer:
        recipients.append(ticket.customer)

    if ticket.assigned_engineer:
        recipients.append(ticket.assigned_engineer)

    # Notify all dispatchers
    from accounts.models import User
    dispatchers = User.objects.filter(role='dispatcher')
    recipients.extend(dispatchers)

    # Remove duplicates while preserving order
    seen = set()
    unique = []
    for u in recipients:
        if u.id not in seen:
            seen.add(u.id)
            unique.append(u)
    return unique


# ===== EMAIL NOTIFICATIONS =====

def send_ticket_email(ticket, notification_type, message):
    """
    Send email notification about ticket.
    Uses SMTP settings from settings.py.
    Logs result to EmailLog model.
    """
    email = None
    if ticket.customer and ticket.customer.email:
        email = ticket.customer.email
    elif hasattr(ticket, 'guest_email') and ticket.guest_email:
        email = ticket.guest_email

    if not email:
        return

    subject = f'ТатАИСнефть — Заявка #{ticket.ticket_number}'
    body = (
        f'Уважаемый клиент!\n\n'
        f'{message}\n\n'
        f'Номер заявки: {ticket.ticket_number}\n'
        f'Статус: {ticket.get_status_display()}\n'
        f'Дата: {ticket.created_at.strftime("%d.%m.%Y %H:%M")}\n\n'
        f'С уважением,\n'
        f'ООО "ТатАИСнефть"\n'
        f'Тел: +7 (8553) 30-50-00\n'
        f'https://tatais.ru'
    )

    try:
        send_mail(
            subject=subject,
            message=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )
        EmailLog.objects.create(
            recipient=email, subject=subject, body=body, status='sent'
        )
        logger.info(f'Email sent to {email}')
    except Exception as e:
        error_msg = str(e)[:200]
        EmailLog.objects.create(
            recipient=email, subject=subject, body=body, status=f'failed: {error_msg}'
        )
        logger.error(f'Email to {email} failed: {error_msg}')


def send_email_direct(email, subject, body):
    """Send a direct email (not tied to a ticket). Useful for password reset, etc."""
    try:
        send_mail(
            subject=subject,
            message=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )
        EmailLog.objects.create(
            recipient=email, subject=subject, body=body, status='sent'
        )
    except Exception as e:
        EmailLog.objects.create(
            recipient=email, subject=subject, body=body, status=f'failed: {str(e)[:200]}'
        )


# ===== SMS NOTIFICATIONS =====

def send_sms(phone, message):
    """
    Send SMS notification.
    Provider is selected via settings.SMS_PROVIDER:
      - 'console': Log to SMSLog table only (no real sending)
      - 'smsaero': Send via SMSAero.ru API
    """
    provider = getattr(settings, 'SMS_PROVIDER', 'console')

    if provider == 'smsaero':
        _send_sms_smsaero(phone, message)
    else:
        # Console mode - just log
        SMSLog.objects.create(
            phone=phone, message=message, status='console_log'
        )
        logger.info(f'SMS (console): {phone} - {message}')


def _send_sms_smsaero(phone, message):
    """
    Send SMS via SMSAero.ru API v2.
    Docs: https://smsaero.ru/api/
    """
    email = getattr(settings, 'SMSAERO_EMAIL', '')
    api_key = getattr(settings, 'SMSAERO_API_KEY', '')
    sender = getattr(settings, 'SMSAERO_SENDER', 'TatAIS')

    if not email or not api_key:
        SMSLog.objects.create(
            phone=phone, message=message, status='failed: SMSAERO credentials not configured'
        )
        logger.warning('SMSAero not configured - check SMSAERO_EMAIL and SMSAERO_API_KEY in settings')
        return

    # Clean phone number
    clean_phone = phone.replace('+', '').replace('(', '').replace(')', '').replace('-', '').replace(' ', '')
    if clean_phone.startswith('8'):
        clean_phone = '7' + clean_phone[1:]

    url = 'https://gate.smsaero.ru/v2/sms/send'
    data = json.dumps({
        'id': hash(clean_phone + message) % 100000000,
        'number': int(clean_phone),
        'sign': sender,
        'text': message,
        'channel': 'DIRECT',
    }).encode('utf-8')

    req = urllib.request.Request(url, data=data, method='POST')
    req.add_header('Content-Type', 'application/json')
    auth_str = f'{email}:{api_key}'
    import base64
    req.add_header('Authorization', f'Basic {base64.b64encode(auth_str.encode()).decode()}')

    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            result = json.loads(response.read().decode('utf-8'))
            if result.get('success'):
                SMSLog.objects.create(
                    phone=phone, message=message, status='sent',
                    external_id=str(result.get('id', ''))
                )
                logger.info(f'SMS sent to {phone} via SMSAero, id={result.get("id")}')
            else:
                error_msg = result.get('message', 'Unknown error')
                SMSLog.objects.create(
                    phone=phone, message=message, status=f'failed: {error_msg}'
                )
                logger.error(f'SMSAero error: {error_msg}')
    except urllib.error.URLError as e:
        SMSLog.objects.create(
            phone=phone, message=message, status=f'failed: {str(e)[:200]}'
        )
        logger.error(f'SMSAero connection error: {e}')
    except Exception as e:
        SMSLog.objects.create(
            phone=phone, message=message, status=f'failed: {str(e)[:200]}'
        )
        logger.error(f'SMSAero error: {e}')
