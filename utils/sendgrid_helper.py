import os
import logging

# Try to import SendGrid, mark as unavailable if not installed
SENDGRID_AVAILABLE = False
try:
    from sendgrid import SendGridAPIClient
    from sendgrid.helpers.mail import Mail
    SENDGRID_AVAILABLE = True
except ImportError:
    SENDGRID_AVAILABLE = False

def send_notification_email(subject: str, body: str) -> bool:
    """
    Send email notification using SendGrid if configured.
    Returns True if sent successfully, False otherwise.
    """
    if not SENDGRID_AVAILABLE:
        logging.info("SendGrid not available, skipping email notification")
        return False
    
    api_key = os.getenv("SENDGRID_API_KEY")
    to_email = os.getenv("EMAIL_TO")
    from_email = os.getenv("EMAIL_FROM", "noreply@callbunker.example.com")
    
    if not (api_key and to_email):
        logging.info("SendGrid not configured, skipping email notification")
        return False
    
    try:
        sg = SendGridAPIClient(api_key)
        message = Mail(
            from_email=from_email,
            to_emails=to_email,
            subject=subject,
            plain_text_content=body
        )
        
        response = sg.send(message)
        logging.info(f"Email sent successfully: {response.status_code}")
        return True
    except Exception as e:
        logging.error(f"SendGrid error: {e}")
        return False
