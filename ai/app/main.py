from fastapi import FastAPI

from .api.routes import router

app = FastAPI(title="Housing Price Prediction API")
app.include_router(router)
