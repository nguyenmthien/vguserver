import sys, ssl, email
from smtplib import SMTP_SSL as SMTP       # this invokes the secure SMTP protocol (port 465, uses SSL)
# from smtplib import SMTP                  # use this for standard SMTP protocol   (port 25, no encryption)

from email import encoders
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase

SMTP_Host = 'smtp.gmail.com'
MY_ADDRESS = 'spam.team1.groupcd.ee4.vgu@gmail.com'
PASSWORD = "H376r923l84b"

def get_contacts(filename):
    emails = []
    with open(filename, mode='r', encoding='utf-8') as contacts_file:
        for contact in contacts_file:
            emails = contact.split()
    return emails

def send_email_file(filename):
    
    emails = get_contacts(filename)
    print(emails)

    s = SMTP(host=SMTP_Host, port=465)
    s.login(MY_ADDRESS, PASSWORD)

    ex_temp = 26
    ex_humid = 65

    text_subtype = 'plain' # typical values for text_subtype are plain, html, xml
    content = """\
    The temperature is {temp}°C and the humidity is {humid}%.
    """
    subject = "Hi! This is your information for VGU Server"

    try:
        for email in emails:
            msg = MIMEMultipart()
            msg['From'] = MY_ADDRESS
            msg['To'] = email
            msg['Subject'] = subject
            msg.attach(MIMEText(content.format(temp=ex_temp,humid=ex_humid), text_subtype))
            #msg.attach(MIMEText(html, 'html'))
            s.send_message(msg)
            del msg
    except:
        pass

    s.quit()

def send_email_list(emails, filename):
    #emails = list
    #filename = 'contacts.txt'

    context = ssl.create_default_context()
    s = SMTP(host=SMTP_Host, port=465, context=context)
    s.login(MY_ADDRESS, PASSWORD)

    text_subtype = 'plain' # typical values for text_subtype are plain, html, xml
    content = """\
    Your data is stored in the attachment below
    """
    subject = "Hi! This is your information for VGU Server"

    with open(filename, "rb") as attachment:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())

    encoders.encode_base64(part)
    part.add_header(
        "Content-Disposition",
        f"attachment; filename= {filename}",
    )

    try:
        for a_email in emails:
            msg = MIMEMultipart()
            msg['From'] = MY_ADDRESS
            msg['To'] = a_email
            msg['Subject'] = subject
            msg.attach(MIMEText(content, text_subtype))
            msg.attach(part)
            text = msg.as_string()
            s.sendmail(MY_ADDRESS, a_email, text)
            del msg
    except:
        pass

    s.quit()
