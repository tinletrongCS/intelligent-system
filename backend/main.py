import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import engine, Base
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


@app.get("/", tags=["Health Check"])
async def root():
    return {"message": "Welcome to the Intelligent System API!"}

if __name__ == "__main__":
    # Lệnh chạy server: python main.py
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)

app.include_router(auth.router, prefix="/auth", tags=["Authentication"])