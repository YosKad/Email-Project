import os
import re
import sendgrid
from sendgrid.helpers.mail import Mail, Email, To, Content
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import imaplib
import email

load_dotenv()

SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY')
EMAIL_ADDRESS = os.getenv('EMAIL_ADDRESS')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')


def send_email(subject, body, to_email):
    sg = sendgrid.SendGridAPIClient(api_key=SENDGRID_API_KEY)
    from_email = Email(EMAIL_ADDRESS)
    to_email = To(to_email)
    content = Content("text/plain", body)
    message = Mail(from_email, to_email, subject, content)
    response = sg.client.mail.send.post(request_body=message.get())
    print(response.status_code)


def validate_email(email_address):
    pattern = r'^([a-zA-Z0-9._%-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})$'
    if re.match(pattern, email_address):
        return True
    return False


def get_latest_email(keyword):
    mail = imaplib.IMAP4_SSL('imap.gmail.com')
    mail.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
    mail.select('inbox')
    _, search_data = mail.search(None, 'ALL')
    mail_ids = search_data[0]
    latest_email_id = mail_ids.split()[-1]
    _, data = mail.fetch(latest_email_id, '(RFC822)')
    raw_email = data[0][1]
    email_message = email.message_from_bytes(raw_email)
    subject = email_message['Subject']
    if keyword in subject:
        for part in email_message.walk():
            if part.get_content_type() == "text/plain":
                body = part.get_payload(decode=True).decode()
                return (subject, body)
    return None


if __name__ == '__main__':
    sendgrid_api_key = input('Enter your SendGrid API key: ')
    email_address = input(
        'Enter the email address to send the test email to: ')
    keyword = input('Enter the keyword to filter the email: ')

    if not validate_email(email_address):
        print('Invalid email address')
        exit()

    sg = sendgrid.SendGridAPIClient(api_key=sendgrid_api_key)
    from_email = Email(EMAIL_ADDRESS)
    to_email = To(email_address)
    content = Content("text/plain", "Test email from SendGrid")
    message = Mail(from_email, to_email, "SendGrid Test Email", content)
    response = sg.client.mail.send.post(request_body=message.get())
    print(response.status_code)

    latest_email = get_latest_email(keyword)
    if latest_email is None:
        print(f"No matching emails found with keyword '{keyword}'")
    else:
        subject, body = latest_email
        print(f"Latest email found with subject '{subject}' and body '{body}'")
