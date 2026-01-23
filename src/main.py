from fastapi import FastAPI,BackgroundTasks,Request,HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import os,logging

from src.configurations.env_var_config import ENV
from src.configurations.logging_config import setup_logging
from src.configurations.limiter_config import limiter
from src.core.lifespan import lifespan

setup_logging()

logger = logging.getLogger(__name__)

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins = ["*"],
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"]
)

@app.get("/",tags=["Health Check"])
def health():
    return {"status":"ok"}

@app.post("/message",tags=["Message"])
@limiter.limit("5/minute")
def send_message(request: Request, name: str, email: str, content: str, bg_task: BackgroundTasks):
    try:
        bg_task.add_task(send_email, name, email, content)

        logger.info("Message sent")
        return {"message":f"Message sent from {name}"}
    except HTTPException:
        logger.info(f"Failed to send the message from: {name}")
        raise
    except Exception as e:
        logger.info(f"Internal Server Error | Failed to send the message from: {name}")
        raise HTTPException(status_code=500,detail="Internal Server Error") from e

APP_PASSWORD = os.getenv("APP_PASSWORD")
def send_email(name: str, email: str, content: str):
    try:
        message = Mail(
            from_email="lagawan0831@gmail.com",
            to_emails="arvenlagawan0731@gmail.com",
            subject="Connect Message",
            plain_text_content=f"Name: {name}\nEmail: {email}\n\nMessage:\n{content}"
        )
        sg = SendGridAPIClient(os.getenv("SENDGRID_API_KEY"))
        response = sg.send(message)

        logger.info(f"Email sent via SendGrid | Status: {response.status_code}")

    except Exception as e:
        logger.error(f"SendGrid email failed: {e}")