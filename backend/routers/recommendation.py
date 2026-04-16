from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from dependencies.auth_deps import get_current_user
from services import recommendation_service
from schemas.product_schema import ProductResponse
from models.user_model import User
from typing import List
from uuid import UUID
from schemas.recommendation_schema import UserRecommendationResponse
from schemas.recommendation_schema import PastRecommendationResponse

router = APIRouter(prefix="/predict", tags=["Recommendation"])

@router.get("/{user_id}", response_model=List[UserRecommendationResponse])
async def predict_user_recommendations(
    user_id: UUID,
    k: int = 10,
    db: Session = Depends(get_db)
):
    """
    API dự đoán sản phẩm gợi ý dựa trên giỏ hàng và wishlist của User.
    Sắp xếp ưu tiên theo Rank (Feedback) trước, sau đó đến Score (AI).
    """
    return await recommendation_service.get_recommendations_for_user(user_id, k, db)


@router.get("/history/{user_id}/{version_id}", response_model=List[PastRecommendationResponse]) # ĐỔI Ở ĐÂY
async def get_recommendation_history(
    user_id: UUID,
    version_id: UUID,
    db: Session = Depends(get_db)
):
    """
    API lấy lại lịch sử gợi ý. 
    Dữ liệu trả về sẽ có dạng: {"product_id": ..., "product_details": {...}}
    """
    return await recommendation_service.get_past_recommendations_logic(user_id, version_id, db)