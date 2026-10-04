from fastapi import FastAPI
from backend.routers import nood
from backend.storage import init_db

app = FastAPI(title="VeiligThuis Backend API")

init_db()
app.include_router(nood.router)

@app.get("/")
def home():
    return {"status": "online", "service": "VeiligThuis API"}
