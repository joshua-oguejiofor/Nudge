import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr

from flask import render_template_string

from app.config import settings

logger = logging.getLogger(__name__)


def send_email(html_body, subject):
    msg = MIMEMultipart("alternative")

    msg["Subject"] = subject
    msg["From"] = formataddr(("Nudge", settings.SMTP_USER))
    msg["To"] = settings.TO_USER

    msg.attach(MIMEText(html_body, "html"))

    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.sendmail(settings.SMTP_USER, settings.TO_USER, msg.as_string())

        return True

    except Exception:
        logger.exception("Error while sending email to.")
        return False
    
    
    
    
def send_todo_reminder(todo_list):
    subject = "Nudge: your tasks for today"
    
    html_template = """
    <div style="max-width: 600px; margin: 40px auto; padding: 30px;
        background-color: #f4f6f8; font-family: Arial, Helvetica, sans-serif; color: #333333; border-radius: 10px;">
        
        <div style="background-color: #ffffff; padding: 30px; border-radius: 8px; text-align: center;">
            <h2 style="margin: 0 0 20px; color: #2563eb; font-size: 24px;">
                Task Reminder
            </h2>
            
            <p style="margin: 0 0 15px; font-size: 16px; line-height: 1.6; color: #555555;">
                Hello, here are your pending tasks for today:
            </p>

            {% if todo_list %}
                <table style="width: 100%; border-collapse: collapse; margin: 20px 0; text-align: left;">
                    <thead>
                        <tr style="border-bottom: 2px solid #ddd;">
                            <th style="padding: 8px;">S/N</th>
                            <th style="padding: 8px;">Title</th>
                            <th style="padding: 8px;">Priority</th>
                            <th style="padding: 8px;">Status</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for todo in todo_list %}
                            <tr style="border-bottom: 1px solid #eee;">
                                <td style="padding: 8px;">{{ loop.index }}</td>
                                <td style="padding: 8px;">{{ todo.title }}</td>
                                <td style="padding: 8px;">{{ todo.priority.name.title() }}</td>
                                <td style="padding: 8px;">{{ 'Completed' if todo.completed else 'Pending' }}</td>
                            </tr>
                        {% endfor %}
                    </tbody>
                </table>
            {% else %}
                <p>You have no tasks pending. Great job!</p>
            {% endif %}

            <p style="margin: 20px 0 0; font-size: 14px; color: #888888;">
                Don't forget to stay on top of your goals!
            </p>
        </div>

        <p style="margin: 20px 0 0; text-align: center; font-size: 12px; color: #999999;">
            Nudge
        </p>
    </div>
    """

    # Render the string template using Jinja via Flask context
    html_content = render_template_string(html_template, todo_list=todo_list)

    return send_email(html_content, subject)


def send_otp_email(otp_code, subject):
    
    
    html_content = f"""
    <div style="max-width: 600px; margin: 40px auto; padding: 30px;
        background-color: #f4f6f8; font-family: Arial, Helvetica, sans-serif; color: #333333; border-radius: 10px;">
        
        <div style="background-color: #ffffff; padding: 30px; border-radius: 8px; text-align: center;">
            <h2 style="margin: 0 0 20px; color: #2563eb; font-size: 24px;">
                Your Verification Code
            </h2>

            <p style="margin: 0 0 15px; font-size: 16px; line-height: 1.6; color: #555555;">
                Hello, use the code below to complete your authentication process:
            </p>

            <div style="margin: 25px 0; padding: 15px; background-color: #eff6ff; border-radius: 6px; display: inline-block;">
                <span style="font-size: 32px; font-weight: bold; letter-spacing: 6px; color: #2563eb;">
                    {otp_code}
                </span>
            </div>

            <p style="margin: 15px 0 0; font-size: 14px; color: #888888;">
                This code will expire shortly. Do not share it with anyone.
            </p>
            
        </div>

        <p style="margin: 20px 0 0; text-align: center; font-size: 12px; color: #999999;">
            Nudge Security Team
        </p>
    </div>
    """
    return send_email(html_content, subject)

    