from datetime import timedelta  
from celery import shared_task  
from django.conf import settings  
from django.core.mail import send_mail  
from django.db import transaction  
from django.template.loader import render_to_string  
from django.utils import timezone  
import sentry_sdk  
 
from .models import EmailOutbox  
 
MAX_ATTEMPTS = 5  
INITIAL_DELAY_SECONDS = 30  
BACKOFF_MULTIPLIER = 2  

def _backoff_seconds(attempts):  
    if attempts <= 0:  
        return 0  
    return int(INITIAL_DELAY_SECONDS * (BACKOFF_MULTIPLIER ** (attempts - 1)))  

def _render_body(template_name, payload):  
    template_path = 'emails/{}.txt'.format(template_name)  
    return render_to_string(template_path, payload)  

def _send_message(message):  
    now = timezone.now()  
    try:  
        payload = dict(message.payload or {})  
        payload.setdefault('whatsapp_link', getattr(settings, 'WHATSAPP_CONTACT_LINK', 'https://wa.me/639171234567?text=Hello'))  
        body = _render_body(message.template, payload)  
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'no-reply@pottershouse.com')  
        send_mail(  
            message.subject,  
            body,  
            from_email,  
            [message.to_email],  
            fail_silently=False,  
        ) 
    except Exception as exc:  
        message.attempts = message.attempts + 1  
        message.status = 'failed'  
        message.last_attempt_at = now  
        message.save(update_fields=['attempts', 'status', 'last_attempt_at', 'updated_at'])  
        if message.attempts > 3:  
            with sentry_sdk.push_scope() as scope:  
                scope.set_context('email_outbox', {  
                    'email_outbox_id': str(message.id),  
                    'to_email': message.to_email,  
                    'attempts': message.attempts,  
                })  
                sentry_sdk.capture_message('Email outbox failed more than 3 times', level='error')  
        return False  
    message.status = 'sent'  
    message.sent_at = now  
    message.last_attempt_at = now  
    message.save(update_fields=['status', 'sent_at', 'last_attempt_at', 'updated_at'])  
    return True  

@shared_task  
def process_email_outbox(limit=50):  
    now = timezone.now()  
    with transaction.atomic():  
        messages = list(  
            EmailOutbox.objects.select_for_update(skip_locked=True)  
            .filter(status__in=['queued', 'failed'])  
            .order_by('created_at')[:limit]  
        )  
    for message in messages:  
        if message.attempts >= MAX_ATTEMPTS:  
            continue  
        if message.status == 'failed' and message.last_attempt_at:  
            delay = _backoff_seconds(message.attempts)  
            if delay and now < message.last_attempt_at + timedelta(seconds=delay):  
                continue  
        _send_message(message)  
 
@shared_task  
def dispatch_outbox():  
    process_email_outbox.delay() 
