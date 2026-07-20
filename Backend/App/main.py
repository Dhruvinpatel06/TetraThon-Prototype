from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from . import models, schemas
from .database import Base, engine, get_db
from .seed import seed
from .routers import advisory, rules, health, locations, crops, post_harvest

app = FastAPI(title="ArgiTech API")

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


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    seed()