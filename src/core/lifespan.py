from fastapi import FastAPI,Request
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
from contextlib import asynccontextmanager
import logging

from src.configurations.limiter_config import limiter
from src.configurations.env_var_config import ENV

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):

    #==================================
        #VALIDATE ENV VARIABLES
    #==================================
    required_env = ["APP_PASSWORD"]
    for variable in required_env:
        if not variable:
            raise RuntimeError(f"Missing environment variable: {variable}")

    #==================================
        #CONFIGURE RATE LIMITER
    #==================================
    app.state.limiter = limiter

    @app.exception_handler(RateLimitExceeded)
    def rate_limit_handler(request: Request, exc: RateLimitExceeded):
        return JSONResponse(status_code=429,content={"message":"Too many request"})
    
    logger.info("Application startup complete")
    yield
    logger.info("Applicaton shutdown")