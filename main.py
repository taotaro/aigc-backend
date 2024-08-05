import uvicorn

from app import create_app
from fastapi import FastAPI
from app.api import router as root_router

app = create_app()

import ssl
import smtplib

# Context to bypass SSL certificate verification
context = ssl._create_unverified_context()

# Your email sending function
server = smtplib.SMTP_SSL('smtp.example.com', 465, context=context)
server.login('username', 'password')
server.sendmail('from@example.com', 'to@example.com', 'email_body')
server.quit()





if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)