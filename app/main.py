import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.routes.flyer import router as flyer_router
from app.logger_config import setup_logging
setup_logging()


app = FastAPI()

OUTPUTS_DIR = "outputs"
os.makedirs(OUTPUTS_DIR, exist_ok=True)
app.mount("/outputs", StaticFiles(directory=OUTPUTS_DIR), name="outputs")


app.include_router(flyer_router, prefix="/api", tags=["Flyer"])

@app.get("/")
async def root():
    return {"message": "Welcome to the Template Generate API!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
