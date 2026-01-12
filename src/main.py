from fastapi import FastAPI
from email.message import EmailMessage
import smtplib

from src.schemas import schemas

app = FastAPI()

@app.get("/")
def app_started():
    return {"message":"App Started"}

@app.post("/message")
async def send_email(message: schemas.Message):
    msg = EmailMessage()
    msg.set_content(f"Name: {message.name} \nEmail: {message.email} \nContent: {message.content}")
    msg["Subject"] = "Connect Message"
    msg["From"] = "lagawan0831@gmail.com"
    msg["To"] = "arvenlagawan0731@gmail.com"

    with smtplib.SMTP_SSL("smtp.gmail.com",465) as server:
        server.login("lagawan0831@gmail.com","wyonximeecjqyjnk")
        server.send_message(msg)