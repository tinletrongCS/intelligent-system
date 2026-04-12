import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import engine, Base
from models import domain_models
# Import router
from routers import auth

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Intelligent System API",
    description="Backend API cho hệ thống Recommendation",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["Authentication"])

@app.get("/", tags=["Health Check"])
async def root():
    return {"message": "Welcome to the Intelligent System API!"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)

