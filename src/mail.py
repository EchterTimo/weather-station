'''
Logic for sending emails
'''

import smtplib
from email.message import EmailMessage

from config import (
    EMAIL_SMTP_SERVER,
    EMAIL_SMTP_PORT,

    EMAIL_USERNAME,
    EMAIL_PASSWORD,

    EMAIL_FROM,
    EMAIL_TO
)


def send_email(
    subject: str,
    content: str,

    smtp_server: str = EMAIL_SMTP_SERVER,
    smtp_port: int = EMAIL_SMTP_PORT,

    smtp_username: str = EMAIL_USERNAME,
    smtp_password: str = EMAIL_PASSWORD,

    sender: str = EMAIL_FROM,
    recipient: str = EMAIL_TO
) -> bool:
    '''
    Send an email
    '''
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = recipient
    msg.set_content(content)

    try:
        with smtplib.SMTP_SSL(host=smtp_server, port=smtp_port) as server:
            server.login(smtp_username, smtp_password)
            server.send_message(msg)
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False
