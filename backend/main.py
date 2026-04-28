import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from database import engine, Base
from database import SessionLocal
from models.user_model import User, Role
from core.security import get_password_hash
# Import router
# from routers import model_ai  # Temporarily commented to avoid installing all ML dependencies
from routers import auth, product, wishlist, cart, order, dashboard, user
from routers import recommendation
from routers import feedback

Base.metadata.create_all(bind=engine)


def ensure_default_admin():
    db = SessionLocal()
    try:
        admin = db.query(User).filter(User.username == "quangkhaiadmin").first()
        if admin:
            admin.role_id = Role.ADMIN
            admin.password_hash = get_password_hash("123456")
        else:
            admin = User(
                username="quangkhaiadmin",
                email="quangkhaiadmin@example.com",
                password_hash=get_password_hash("123456"),
                role_id=Role.ADMIN,
            )
            db.add(admin)
        db.commit()
    finally:
        db.close()


ensure_default_admin()

app = FastAPI(
    title="Intelligent System API",
    description="Backend API cho hệ thống Recommendation",
    version="1.0.0"
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
IMAGES_DIR = PROJECT_ROOT / "data_scientist" / "images"

if IMAGES_DIR.exists():
    app.mount("/images", StaticFiles(directory=str(IMAGES_DIR)), name="images")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
# app.include_router(model_ai.router)  # Temporarily disabled
app.include_router(product.router, prefix="/products", tags=["Products"])
app.include_router(wishlist.router, prefix="/wishlist", tags=["Wishlist"])
app.include_router(cart.router, prefix="/cart", tags=["Cart"])
app.include_router(order.router)
app.include_router(dashboard.router)
app.include_router(user.router, prefix="/users", tags=["Users"])
app.include_router(recommendation.router)
app.include_router(feedback.router)

@app.get("/", tags=["Health Check"])
async def root():
    return {"message": "Welcome to the Intelligent System API!"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)
