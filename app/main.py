from contextlib import asynccontextmanager
from fastapi import FastAPI

from database import engine #, init_db
from routers import conversations


@asynccontextmanager
async def lifespan(_: FastAPI):
#     await init_db()
    yield
#     await engine.dispose()


app = FastAPI(lifespan=lifespan)

app.include_router(conversations.router)

