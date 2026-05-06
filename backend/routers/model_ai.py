from fastapi import APIRouter, Depends, BackgroundTasks, status, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from services import model_ai_service
from services.model_ai_service import AIPipelineService

router = APIRouter()

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

@router.get("/reports/original/latest")
async def get_latest_original_report(db: Session = Depends(get_db)):
    """
    API lấy báo cáo EDA dữ liệu gốc (Original) của phiên bản mới nhất.
    """
    service = AIPipelineService(db)
    data, error = await service.get_latest_eda_report_service("original")
    
    if error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error)
    
    return data

@router.get("/reports/normalized/latest")
async def get_latest_normalized_report(db: Session = Depends(get_db)):
    """
    API lấy báo cáo EDA dữ liệu chuẩn hóa (Normalized) của phiên bản mới nhất.
    """
    service = AIPipelineService(db)
    data, error = await service.get_latest_eda_report_service("normalized")
    
    if error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error)
    
    return data
