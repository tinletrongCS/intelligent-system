from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from dependencies.auth_deps import get_current_user
from services import recommendation_service
from schemas.product_schema import ProductResponse
from models.user_model import User
from typing import List

router = APIRouter(prefix="/predict", tags=["Recommendation"])

@router.get("/{user_id}", response_model=List[ProductResponse])
async def predict_user_recommendations(
    user_id: str,
    k: int = 10,
    db: Session = Depends(get_db)
    # current_user: User = Depends(get_current_user)
):
    """
    API dự đoán sản phẩm gợi ý dựa trên giỏ hàng và wishlist của User.
    """
    return await recommendation_service.get_recommendations_for_user(user_id, k, db)