from dotenv import load_dotenv

load_dotenv()
from fastapi import FastAPI
from api.routers import health

app = FastAPI()

app.include_router(health.router)


@app.get("/")
async def root():
    return {"message": "Hello World"}
