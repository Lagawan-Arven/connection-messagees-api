from fastapi import FastAPI,BackgroundTasks,Request,HTTPException
from fastapi.middleware.cors import CORSMiddleware
from email.message import EmailMessage
import smtplib,os,logging

from src.schemas import schemas
from src.configurations.env_var_config import ENV
from src.configurations.logging_config import setup_logging
from src.configurations.limiter_config import limiter
from src.core.lifespan import lifespan

setup_logging()

logger = logging.getLogger(__name__)

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins = ["https://lagawan-arven.github.io/Arven-Lagawan/#Contact"],
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"]
)

@app.get("/",tags=["Health Check"])
def health():
    return {"status":"ok"}

@app.post("/message",tags=["Message"])
@limiter.limit("5/minute")
def send_message(request: Request, message: schemas.Message, bg_task: BackgroundTasks):
    try:
        msg = EmailMessage()
        msg.set_content(f"Name: {message.name} \nEmail: {message.email} \nContent: {message.content}")
        msg["Subject"] = "Connect Message"
        msg["From"] = "lagawan0831@gmail.com"
        msg["To"] = "arvenlagawan0731@gmail.com"

        bg_task.add_task(send_email,msg)
        logger.info("Message sent")
        return {f"message":"Message sent from {message.name}"}
    except HTTPException:
        logger.info(f"Failed to send the message from: {message.name}")
        raise
    except Exception as e:
        logger.info(f"Internal Server Error | Failed to send the message from: {message.name}")
        raise HTTPException(status_code=500,detail="Internal Server Error") from e

APP_PASSWORD = os.getenv("APP_PASSWORD")
def send_email(message):
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com",465) as server:
            server.login("lagawan0831@gmail.com",APP_PASSWORD)
            server.send_message(message)
    except:
        logger.info("Failed to send the email")
        raise HTTPException(status_code=417,detail="Failed to send the email")
