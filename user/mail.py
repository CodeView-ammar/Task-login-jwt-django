import smtplib
from email.message import EmailMessage
import codecs
from typing import *
from datetime import datetime
import logging
from django.conf import settings
EMAIL_HOST = settings.EMAIL_HOST
EMAIL_HOST_USER =  settings.EMAIL_HOST_USER
EMAIL_HOST_PASSWORD = settings.EMAIL_HOST_PASSWORD
EMAIL_PORT = settings.EMAIL_PORT

HTMLFile = codecs.open("template/mail_template.html", 'r', "utf-8").read()
def send_verify_email(user, link):
    content = f"Hi there, {user.first_name} {user.last_name} We received a request to create a new account with your email address. To confirm that this is you, please enter the following verification code when prompted"
    title = 'Email Verification'
    index = HTMLFile.format(title=title,link=link,content=content)
    logging.getLogger().error(link) 
    with smtplib.SMTP_SSL(EMAIL_HOST, EMAIL_PORT) as smtp:
        smtp.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD) 
        for email in set([user.email]):
            msg = EmailMessage()
            msg['To'] = email
            msg['From'] = EMAIL_HOST_USER 
            msg['Subject'] = "Verify Email Account | ammar wadood" 
            msg.set_content(index,subtype='html')
            smtp.send_message(msg)
        
