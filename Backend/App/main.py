from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import Base, engine
from .seed import seed
from .routers import advisory, rules, health, locations, crops, post_harvest, leaf_classify

app = FastAPI(title="AgriTech API")

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    seed()
    yield


app = FastAPI(title="AgriTech API", lifespan=lifespan)

app.include_router(advisory.router, prefix="/api")
app.include_router(rules.router, prefix="/api")
app.include_router(health.router, prefix="/api")
app.include_router(locations.router, prefix="/api")
app.include_router(crops.router, prefix="/api")
app.include_router(post_harvest.router, prefix="/api")
app.include_router(leaf_classify.router, prefix="/api", tags=["leaf-classify"])

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)