from sqlalchemy.orm import Session
from fastapi import HTTPException
from uuid import UUID
from models.interaction_model import Interaction, InteractionType
import repositories.cart_repository as cart_repo

async def add_product_to_cart(user_id: UUID, product_id: UUID, request_quantity: int, db: Session):
    product = cart_repo.check_product_exists(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Sản phẩm không tồn tại")
    if request_quantity > product.quantity_in_stock:
        raise HTTPException(status_code=409, detail="Vượt quá số lượng còn trong kho")
    # trừ số lượng kho - ko commit 
    product.quantity_in_stock -= request_quantity

    # thêm vào cart - ko commit
    cart_item = cart_repo.add_product_to_cart_no_commit(db, user_id, product_id, request_quantity)
    if not cart_item:
        db.rollback()
        raise HTTPException(status_code=500, detail="Thêm sản phẩm vào giỏ hàng thất bại")
    # ghi log interaction - ko commit 
    
    interaction = Interaction(
        user_id=user_id,
        product_id=product_id,
        interaction_type=InteractionType.ADDED_TO_CART)
    db.add(interaction)
    # Commit toàn bộ transaction 
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Lỗi hệ thống: không thể thêm vào giỏ hàng")

    return cart_item