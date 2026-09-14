from contextlib import asynccontextmanager

from fastapi import FastAPI

from app import models  # noqa: F401  (registers models on Base.metadata)
from app.database import Base, engine
from app.routers import auth, health, slots


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="Booking App API", lifespan=lifespan)

app.include_router(health.router)
app.include_router(auth.router)
app.include_router(slots.router)
