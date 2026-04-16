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
from models.recommendation_model import UserRecommendation
from models.feedback_model import Feedback

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
    
    # 2. Lấy thông tin Model active
    active_version = db.query(ModelVersion).filter(ModelVersion.is_active == True).first()
    id_csv_path = base_dir / "data_scientist" / "features" / "image_features" / "image_feature_ids.csv"
    
    if active_version:
        rec_repo.delete_recommendations_by_user_and_version(db, user_id, active_version.id)

    def format_fallback_products(products):
        return [{
            "product_id": p.id,
            "score": 0.0,
            "rank": 5,
            "product_details": p
        } for p in products]

    if not active_version or not id_csv_path.exists():
        products = db.query(Product).order_by(Product.created_at.desc()).limit(k).all()
        return format_fallback_products(products)

    # 3. Load Embeddings và tính Similarity
    all_embeddings = np.load(str(base_dir / active_version.gnn_emb_path))
    user_indices = get_product_indices(user_product_ids, id_csv_path)
    
    if not user_indices:
        products = db.query(Product).order_by(Product.created_at.desc()).limit(k).all()
        return format_fallback_products(products)

    user_vector = np.mean(all_embeddings[user_indices], axis=0).reshape(1, -1)
    similarities = cosine_similarity(user_vector, all_embeddings)[0]

    # 4. Lấy Rank từ bảng Feedback của chính User này
    df_ids = pd.read_csv(id_csv_path)
    all_product_uuids = [UUID(id_str) for id_str in df_ids['id'].tolist()]
    
    user_feedbacks = db.query(Feedback.product_id, Feedback.rank).filter(Feedback.user_id == user_id).all()
    feedback_map = {f.product_id: f.rank for f in user_feedbacks}
    
    # Rank mặc định là 5 nếu chưa có feedback
    product_ranks = np.array([feedback_map.get(uid, 5) for uid in all_product_uuids])

    # 5. Sắp xếp 2 cấp: Rank giảm dần, sau đó Score giảm dần
    sorted_indices = np.lexsort((-similarities, -product_ranks))

    recommended_metadata = []
    recommended_ids_only = []

    for idx in sorted_indices:
        p_id = all_product_uuids[idx]
        current_rank = int(product_ranks[idx])
        
        if p_id not in user_product_ids:
            recommended_metadata.append({
                "product_id": p_id,
                "score": float(similarities[idx]),
                "rank": current_rank
            })
            recommended_ids_only.append(p_id)
        
        if len(recommended_metadata) >= k:
            break

    # 6. Truy vấn thông tin sản phẩm (Bulk Query)
    products_db = db.query(Product).filter(Product.id.in_(recommended_ids_only)).all()
    product_map = {p.id: p for p in products_db}

    # 7. Đóng gói kết quả và lưu Log
    final_response = []
    recs_to_log = []

    for item in recommended_metadata:
        p_id = item["product_id"]
        p_obj = product_map.get(p_id)
        if not p_obj: continue

        result_item = {
            "product_id": p_id,
            "score": item["score"],
            "rank": item["rank"],
            "product_details": p_obj
        }
        final_response.append(result_item)

        recs_to_log.append(UserRecommendation(
            user_id=user_id,
            product_id=p_id,
            score=item["score"],
            rank=item["rank"],
            version_id=active_version.id
        ))

    if recs_to_log:
        rec_repo.save_user_recommendations(db, recs_to_log)

    return final_response


async def get_product_user_recommendations(user_id: UUID, version_id: UUID, db: Session):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Người dùng không tồn tại")

    version = db.query(ModelVersion).filter(ModelVersion.id == version_id).first()
    if not version:
        raise HTTPException(
            status_code=404, 
            detail=f"Phiên bản Model với ID {version_id} không tồn tại trong hệ thống"
        )

    past_recs = rec_repo.get_recommendations_by_user_and_version(db, user_id, version_id)
    if not past_recs:
        return []

    product_ids = [rec.product_id for rec in past_recs]
    products = db.query(Product).filter(Product.id.in_(product_ids)).all()
    product_map = {p.id: p for p in products}

    final_results = []
    for pid in product_ids:
        if pid in product_map:
            final_results.append({
                "product_id": pid,
                "product_details": product_map[pid]
            })

    return final_results


async def get_products_recommendation(product_id: UUID, version_id: UUID, k: int, db: Session):
    target_product = db.query(Product).filter(Product.id == product_id).first()
    if not target_product:
        raise HTTPException(status_code=404, detail=f"Sản phẩm ID {product_id} không tồn tại")

    version = db.query(ModelVersion).filter(ModelVersion.id == version_id).first()
    if not version:
        raise HTTPException(status_code=404, detail=f"Phiên bản Model ID {version_id} không tồn tại")

    recommendations = db.query(UserRecommendation).filter(
        UserRecommendation.product_id == product_id,
        UserRecommendation.version_id == version_id
    ).limit(k).all()

    if not recommendations:
        return []

    final_response = []
    for rec in recommendations:
        final_response.append({
            "product_id": rec.product_id,
            "score": rec.score,
            "rank": rec.rank,
            "product_details": target_product
        })

    return final_response