from fastapi import APIRouter, Depends, BackgroundTasks, status
from sqlalchemy.orm import Session
from database import get_db
from services import model_ai_service

router = APIRouter(prefix="/ai", tags=["AI Pipeline"])

@router.post("/trigger-training", status_code=status.HTTP_202_ACCEPTED)
async def trigger_ai_pipeline(
    background_tasks: BackgroundTasks, 
    db: Session = Depends(get_db)
):
    """
    Endpoint kích hoạt quy trình huấn luyện AI. 
    Trả về 202 ngay lập tức và xử lý training dưới nền.
    """
    return await model_ai_service.trigger_training_service(db, background_tasks)