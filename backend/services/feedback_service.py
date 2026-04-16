from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from uuid import UUID
from models.interaction_model import Interaction, InteractionType
import repositories.feedback_repository as feedback_repo
from models.user_model import User
from models.product_model import Product

async def submit_feedback_logic(user_id: UUID, product_id: UUID, rank: int, db: Session):
    # 1. Lưu feedback vào database
    feedback = feedback_repo.create_or_update_feedback(db, user_id, product_id, rank)
    
    if not feedback:
        raise HTTPException(status_code=500, detail="Không thể lưu feedback")

    # 2. Ghi nhận Interaction để GNN học tập
    # Bạn có thể quy ước InteractionType.RATED cho điểm số
    interaction = Interaction(
        user_id=user_id,
        product_id=product_id,
        interaction_type=InteractionType.VIEWED # Hoặc InteractionType.RATED nếu bạn đã định nghĩa
    )
    db.add(interaction)
    db.commit()

    return feedback

async def get_user_feedbacks_logic(user_id: UUID, db: Session):
    """Logic lấy danh sách đánh giá của người dùng với bước check tồn tại"""
    # 1. Kiểm tra User có tồn tại không
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Người dùng với ID {user_id} không tồn tại"
        )
    
    # 2. Nếu tồn tại thì mới gọi repo lấy dữ liệu
    return feedback_repo.get_feedbacks_by_user(db, user_id)


async def get_product_feedbacks_logic(product_id: UUID, db: Session):
    """Logic lấy danh sách đánh giá của sản phẩm với bước check tồn tại"""
    # 1. Kiểm tra Sản phẩm có tồn tại không
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sản phẩm với ID {product_id} không tồn tại"
        )
    
    # 2. Nếu tồn tại thì mới gọi repo lấy dữ liệu
    return feedback_repo.get_feedbacks_by_product(db, product_id)