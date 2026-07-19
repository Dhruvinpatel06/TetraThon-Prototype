from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from . import models, schemas
from .database import Base, engine, get_db
from .seed import seed
from .routers import advisory, rules

app = FastAPI(title="TetraTHON AgriTech API")

app.include_router(advisory.router)
app.include_router(rules.router)


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


@app.get("/health")
def health():
    return {"status": "OK"}


@app.get("/locations", response_model=list[schemas.LocationOut])
def get_locations(db: Session = Depends(get_db)):
    return db.query(models.Location).all()


@app.get("/crops", response_model=list[schemas.CropOut])
def get_crops(db: Session = Depends(get_db)):
    return db.query(models.Crop).all()