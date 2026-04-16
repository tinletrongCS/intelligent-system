import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from pathlib import Path
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List
from fastapi import HTTPException, status

from models.user_model import User
from models.cart_model import Cart
from models.wishlist_model import Wishlist
from models.product_model import Product
from models.model_ai_model import ModelVersion
from models.recommendation_model import UserRecommendation
import repositories.recommendation_repository as rec_repo
from models.recommendation_model import UserRecommendation, ProductPriority

base_dir = Path(__file__).resolve().parent.parent.parent

def get_product_indices(product_uuids: List[UUID], id_csv_path: Path) -> List[int]:
    """Hàm ánh xạ UUID sản phẩm sang Index trong ma trận embeddings"""
    if not id_csv_path.exists():
        return []
    df_ids = pd.read_csv(id_csv_path)
    indices = df_ids[df_ids['id'].isin([str(u) for u in product_uuids])].index.tolist()
    return indices

async def get_recommendations_for_user(user_id: UUID, k: int, db: Session):
    # 0. Kiểm tra User tồn tại
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Người dùng không tồn tại")

    # 1. Lấy sản phẩm tương tác (Cart + Wishlist)
    cart_items = db.query(Cart.product_id).filter(Cart.user_id == user_id).all()
    wishlist_items = db.query(Wishlist.product_id).filter(Wishlist.user_id == user_id).all()
    user_product_ids = list(set([item.product_id for item in (cart_items + wishlist_items)]))
    
    # 2. Lấy thông tin Model active và Mapping ID
    active_version = db.query(ModelVersion).filter(ModelVersion.is_active == True).first()
    id_csv_path = base_dir / "data_scientist" / "features" / "image_features" / "image_feature_ids.csv"
    
    if not active_version or not id_csv_path.exists():
        return db.query(Product).order_by(Product.created_at.desc()).limit(k).all()

    # 3. Load Embeddings và tính Similarity (User-to-Item)
    all_embeddings = np.load(str(base_dir / active_version.gnn_emb_path))
    user_indices = get_product_indices(user_product_ids, id_csv_path)
    
    if not user_indices:
        return db.query(Product).order_by(Product.created_at.desc()).limit(k).all()

    user_vector = np.mean(all_embeddings[user_indices], axis=0).reshape(1, -1)
    similarities = cosine_similarity(user_vector, all_embeddings)[0]

    # 4. Lấy Rank (Priority) từ bảng product_priorities
    df_ids = pd.read_csv(id_csv_path)
    all_product_uuids = [UUID(id_str) for id_str in df_ids['id'].tolist()]
    
    priorities_data = db.query(ProductPriority.product_id, ProductPriority.priority_level).all()
    priority_map = {p.product_id: p.priority_level for p in priorities_data}
    
    product_ranks = np.array([priority_map.get(uid, 5) for uid in all_product_uuids])

    # 5. Sắp xếp: Rank (Priority) trước (5 cao nhất), sau đó mới đến Score
    sorted_indices = np.lexsort((-similarities, -product_ranks))

    recommended_ids = []
    final_recs_to_db = []

    for idx in sorted_indices:
        p_id = all_product_uuids[idx]
        current_rank = int(product_ranks[idx])
        
        if p_id not in user_product_ids:
            final_recs_to_db.append(UserRecommendation(
                user_id=user_id,
                product_id=p_id,
                score=float(similarities[idx]),
                rank=current_rank,
                version_id=active_version.id
            ))
            product_info = db.query(Product).filter(Product.id == p_id).first()
            recommended_ids.append({
                "product_id": p_id,
                "score": float(similarities[idx]),
                "rank": current_rank,
                "product_details": product_info
            })
        
        if len(recommended_ids) >= k:
            break

    # 6. Lưu kết quả và trả về chi tiết sản phẩm
    if final_recs_to_db:
        rec_repo.save_user_recommendations(db, final_recs_to_db)

    # Trả về chi tiết sản phẩm, đảm bảo giữ đúng thứ tự đã sort
    return db.query(Product).filter(Product.id.in_(recommended_ids)).all()