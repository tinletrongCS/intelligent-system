from sqlalchemy.orm import Session
from fastapi import BackgroundTasks, HTTPException, status
from services.model_ai_service import AIPipelineOrchestrator
from datetime import datetime
from repositories import product_repository

async def run_full_process(orchestrator: AIPipelineOrchestrator):
    """
    Hàm xử lý logic chạy ngầm.
    Đã sửa: Truyền version_obj và đồng bộ thứ tự Train -> Archive.
    """
    try:
        print("=== BẮT ĐẦU PIPELINE CHẠY NGẦM ===")
        
        products = product_repository.get_all_products(orchestrator.db, limit=100000)
        actual_count, _ = orchestrator.sync_db_to_ai_input() 

        orchestrator.download_product_images(products)

        v_tag, v_obj = orchestrator.archive_current_version(actual_count)
        
        orchestrator.execute_ai_domino(v_tag, v_obj.id)

        orchestrator.finalize_version_archive(v_tag, v_obj)

        print(f"--- [SUCCESS] Hoàn thành Pipeline AI phiên bản: {v_tag} ---")
        
    except Exception as e:
        orchestrator.db.rollback() # Quan trọng: Rollback nếu lỗi để tránh rác DB
        print(f"--- [ERROR] Lỗi Pipeline trong quá trình chạy nền: {str(e)} ---")


async def trigger_training_controller(db: Session, background_tasks: BackgroundTasks):
    """
    Controller điều phối kích hoạt huấn luyện theo phong cách 'Check and Raise'.
    """
    orchestrator = AIPipelineOrchestrator(db)
    
    # 1. Đồng bộ dữ liệu hiện tại từ DB ra CSV
    count, _ = orchestrator.sync_db_to_ai_input()
    
    # 2. Kiểm tra xem có cần huấn luyện lại không
    is_needed = orchestrator.check_incremental(count)
    
    if not is_needed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Dữ liệu hiện tại ({count} sản phẩm) đã được huấn luyện. Không có thay đổi để cập nhật."
        )
    
    background_tasks.add_task(run_full_process, orchestrator)
    
    return {
        "status": "accepted",
        "message": f"Phát hiện dữ liệu mới. Pipeline AI (với {count} sản phẩm) đã bắt đầu chạy dưới nền.",
        "version_tag": datetime.now().strftime('v_%Y%m%d_%H%M%S')
    }