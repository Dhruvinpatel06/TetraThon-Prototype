from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import Base, engine
from .seed import seed
from .routers import advisory, rules, health, locations, crops, post_harvest


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    seed()
    yield


app = FastAPI(title="ArgiTech API", lifespan=lifespan)

app.include_router(advisory.router)
app.include_router(rules.router)
app.include_router(health.router)
app.include_router(locations.router)
app.include_router(crops.router)
app.include_router(post_harvest.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)