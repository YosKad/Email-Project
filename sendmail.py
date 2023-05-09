import os
import re
import sendgrid
from dotenv import load_dotenv
from sendgrid.helpers.mail import Mail
from bs4 import BeautifulSoup
from jinja2 import Template

load_dotenv()

# Set SendGrid API key
SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY')
sg = sendgrid.SendGridAPIClient(api_key=SENDGRID_API_KEY)

# Email validation function
def validate_email(email):
    response = sg.client.validation.email.get(query_params={'email': email})
    return response.status_code == 200

# Email filtering and sorting function
def filter_emails(emails, keyword):
    filtered_emails = []
    for email in emails:
        subject = email['subject']
        body = email['body']
        if keyword in subject or keyword in body:
            filtered_emails.append(email)
    filtered_emails.sort(key=lambda x: x['date'], reverse=True)
    return filtered_emails

# Email response generation function
def generate_response(email):
    name = email['sender']
    subject = email['subject']
    message = email['body']
    template = Template("""\
        Dear {{ name }},
        Thank you for your email with the subject "{{ subject }}". We have received your message and will get back to you as soon as possible.
        Best regards,
        Email Filtering Tool
    """)
    return template.render(name=name, subject=subject)

# Main function
def main():
    # Retrieve incoming emails using SendGrid's API
    response = sg.client.inbound_emails.get()
    emails = []
    for email in response.body:
        # Parse email contents using Beautiful Soup
        soup = BeautifulSoup(email['html'], 'html.parser')
        sender = soup.find('span', {'data-test-id': 'previewFromLine'}).text
        subject = soup.find('h2', {'data-test-id': 'previewSubject'}).text
        date = soup.find('time', {'data-test-id': 'emailReceivedDate'}).text
        body = soup.find('div', {'data-test-id': 'emailBody'}).text
        # Validate email address
        if validate_email(sender):
            emails.append({'sender': sender, 'subject': subject, 'date': date, 'body': body})
    # Filter and sort emails based on keyword
    keyword = 'important'
    filtered_emails = filter_emails(emails, keyword)
    # Generate response emails and send using SendGrid's API
    for email in filtered_emails:
        recipient = email['sender']
        response = generate_response(email)
        message = Mail(
            from_email='your_email@example.com',
            to_emails=recipient,
            subject='Re: ' + email['subject'],
            html_content=response)
        response = sg.client.mail.send.post(request_body=message.get())
        print(response.status_code)

if __name__ == '__main__':
    main()
