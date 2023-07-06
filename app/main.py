import uvicorn

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers.routes import include_router
from utils.middlewares import include_middlewares

""" To init DB automatically """
# from commons.database.db import Base, engine
# Base.metadata.create_all(bind=engine)

app = FastAPI(title="Twitter API", version="0.0.1")

include_middlewares(app=app)
include_router(app=app)

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
