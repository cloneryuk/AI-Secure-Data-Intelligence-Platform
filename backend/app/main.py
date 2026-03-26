import logging 
import time
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from dotenv import load_dotenv

load_dotenv()

def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"detail": "Rate limit exceeded"},
    )

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s|%(message)s",
    datefmt="%Y-%m_%d %H:%M:%S",

)
logger=logging.getLogger("ai+platform")
limiter=Limiter(key_func=get_remote_address)
@asynccontextmanager
async def lifespan(app:FastAPI):
    logger.info("AI Secure Data Intelligence Platform starting up")
    yield
    logger.info("Shutting down")
app=FastAPI(
    title="AI Secure Data Intelligence Platform",
    description="AI Gateway+Data Scanner +Log Analyzer+Risk Enginer",
    version="1.0.0",
    lifespan=lifespan,
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*",]
)
@app.middleware("http")
async def observablilty_middleware(request:Request,call_next):
    start=time.perf_counter()
    content_length=request.headers.get("content-length","0")
    logger.info(
        "-> %s %s payload=%s bytes,",
        request.method,request.url.path,content_length,
    )
    response =await call_next(request)
    elapsed_ms=(time.perf_counter()-start)*1000
    logger.info(
        "-> %s %s status=%s time=%.1fms",
        request.method,request.url.path, response.status_code,elapsed_ms,
    )
    response.headers["X-Process-Time-Ms"]=f"{elapsed_ms:.1f}"
    return response

@app.get("/")
async def root():
    return {"message": "AI Secure Data Intelligence Platform API is running. Visit /docs for Swagger UI."}

@app.get("/health")
async def health():
    return {"status":"ok","service":"AI Secure Data Intelligence Platform"}

from app.api.routes import router as analyzer_router
app.include_router(analyzer_router)

