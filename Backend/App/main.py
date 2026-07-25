import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from .database import Base, engine
from .seed import seed
from .limiter import limiter
from .routers import advisory, rules, health, locations, crops, post_harvest, leaf_classify

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    if os.getenv("AUTO_SEED", "false").lower() == "true":
        seed()
    yield


from fastapi.responses import JSONResponse

app = FastAPI(
    title="AgriTech API",
    description="Precision Crop Advisory & Post-Harvest Decision Engine API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal server error: {str(exc)}"}
    )

app.add_middleware(SlowAPIMiddleware)

@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response

app.include_router(advisory.router, prefix="/api")
app.include_router(rules.router, prefix="/api")
app.include_router(health.router, prefix="/api")
app.include_router(locations.router, prefix="/api")
app.include_router(crops.router, prefix="/api")
app.include_router(post_harvest.router, prefix="/api")
app.include_router(leaf_classify.router, prefix="/api", tags=["leaf-classify"])

cors_env = os.getenv("CORS_ORIGINS", "")
if cors_env:
    origins = [origin.strip() for origin in cors_env.split(",") if origin.strip()]
else:
    origins = ["http://localhost:5173"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)