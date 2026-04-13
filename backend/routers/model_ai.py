from fastapi import APIRouter, Depends, BackgroundTasks, status
from sqlalchemy.orm import Session
from database import get_db
from services.ai_pipeline_service import AIPipelineOrchestrator

router = APIRouter(prefix="/ai", tags=["AI Pipeline"])

@router.post("/trigger-training", status_code=status.HTTP_202_ACCEPTED)
async def trigger_ai_pipeline(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    orchestrator = AIPipelineOrchestrator(db)
    
    # 1. Đồng bộ dữ liệu
    count, _ = orchestrator.sync_db_to_ai_input()
    
    # 2. Kiểm tra thay đổi
    if orchestrator.check_incremental(count):
        background_tasks.add_task(run_full_process, orchestrator)
        return {"message": "Phát hiện dữ liệu mới. Pipeline AI đã bắt đầu chạy dưới nền."}
    
    return {"message": "Dữ liệu chưa có thay đổi đáng kể. Không cần huấn luyện lại."}

async def run_full_process(orchestrator: AIPipelineOrchestrator):
    try:
        # Bước 4.5 & 4.6 thực hiện trong domino
        v_tag = orchestrator.archive_current_version()
        orche_exec = orchestrator.execute_ai_domino(v_tag)
        print(f"Hoàn thành Pipeline AI phiên bản: {v_tag}")
    except Exception as e:
        print(f"Lỗi Pipeline: {str(e)}")