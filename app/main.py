import uvicorn

from fastapi import FastAPI

from routers.routes import include_router
from config.settings import settings
# from utils.middlewares import include_middlewares

""" To init DB automatically """
# from commons.database.db import Base, engine
# Base.metadata.create_all(bind=engine)

app = FastAPI(title="Twitter API", version="0.0.1")

# include_middlewares(app=app)
include_router(app=app)

if __name__ == "__main__":
    if settings.environment == 'local':
        uvicorn.run("main:app", reload=True)
    else:
        uvicorn.run('main:app')
