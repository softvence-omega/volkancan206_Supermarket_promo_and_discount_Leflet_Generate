from fastapi import FastAPI, Response
import requests
from app.routes.Tamplate import router
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
