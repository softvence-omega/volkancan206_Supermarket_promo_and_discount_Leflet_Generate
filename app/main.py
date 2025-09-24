from fastapi import FastAPI
from app.routes.Tamplate import router
from app.logger_config import setup_logging
setup_logging()



app = FastAPI()

app.include_router(router, prefix="/api", tags=["Campaign"])


# Root route
@app.get("/")
async def root():
    return {"message": "Welcome to the Tamplate Generate API!"}



# Run locally:
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
