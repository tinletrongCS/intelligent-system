import pandas as pd
import numpy as np
import os
import subprocess
import shutil
from datetime import datetime
from sqlalchemy.orm import Session
from repositories import product_repository
from models.product_model import Product
# Giả sử bạn dùng SQLite/PostgreSQL cho model_versions

# Các đường dẫn tương đối để đảm bảo chạy được trên mọi máy
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
data_dir = os.path.join(base_dir, "data_ai", "standard_dataset")
features_dir = os.path.join(data_dir, "features")
models_registry_dir = os.path.join(base_dir, "data_ai", "models")

class AIPipelineOrchestrator:
    def __init__(self, db: Session):
        self.db = db
        # Đảm bảo các thư mục tồn tại trên máy mới
        os.makedirs(data_dir, exist_ok=True)
        os.makedirs(features_dir, exist_ok=True)
        os.makedirs(models_registry_dir, exist_ok=True)

    def sync_db_to_ai_input(self):
        """
        Bước 1: Lấy dữ liệu trực tiếp từ get_all_products và tạo file trung gian
        Điều này giúp đồng bộ hóa thuộc tính từ DB vào AI Script.
        """
        print("--- Đang đồng bộ hóa dữ liệu từ Database ---")
        # Lấy tối đa sản phẩm từ DB
        products = product_repository.get_all_products(self.db, limit=100000)
        
        if not products:
            print("Cảnh báo: Database đang trống, không có gì để trích xuất.")
            return 0

        # Chuyển đổi SQLAlchemy objects sang DataFrame
        # Lưu ý map đúng tên cột mà các script EDA/Preprocessing đang yêu cầu
        data = [{
            "id": str(p.id),
            "brandName": p.brand_name,
            "gender": p.gender,
            "masterCategory": p.master_category,
            "subCategory": p.sub_category,
            "articleType": p.article_type,
            "baseColour": p.base_colour,
            "season": p.season,
            "usage": p.usage,
            "productDisplayName": p.product_display_name,
            "price": p.price,
            "myntraRating": p.myntra_rating or 0.0 # Xử lý null
        } for p in products]

        df = pd.DataFrame(data)
        temp_csv_path = os.path.join(data_dir, "fashion_db_dump.csv")
        df.to_csv(temp_csv_path, index=False)
        print(f"Đã tạo file dữ liệu đầu vào: {len(df)} sản phẩm.")
        return len(df)

    def check_incremental(self, current_count):
        """Bước 2: So sánh với Mapping hiện tại để quyết định có train lại không"""
        mapping_path = os.path.join(features_dir, "edge_matrix_features", "id_to_idx_mapping.csv")
        if not os.path.exists(mapping_path):
            return True # Máy mới hoàn toàn, cần chạy AI
            
        old_mapping = pd.read_csv(mapping_path)
        return current_count > len(old_mapping)

    async def execute_ai_domino(self):
        """Bước 3: Chạy chuỗi Domino AI"""
        scripts = [
            "1_EDA_original.py", "2_preprocessing.py", "3_EDA_normalized.py",
            "4_1_image_extractor.py", "4_2_metadata_extractor.py", "4_3_text_extractor.py",
            "4_4_feature_fusion.py", "4_5_matrix_edges.py", "4_6_train_GNN.py"
        ]
        
        for script in scripts:
            print(f">>> Thực thi: {script}")
            # Chạy script Python (đảm bảo môi trường ảo đã được kích hoạt)
            process = subprocess.run(["python", script], capture_output=True, text=True)
            if process.returncode != 0:
                print(f"LỖI tại {script}: {process.stderr}")
                return False
        return True

    def archive_current_version(self):
        """Bước 4: Đóng gói và lưu trữ toàn bộ file trọng số và đặc trưng"""
        version_id = f"v_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        v_dir = os.path.join(models_registry_dir, version_id)
        os.makedirs(v_dir, exist_ok=True)

        # Lưu trọn bộ để đảm bảo tính nhất quán (Consistency)
        files_to_save = {
            "image_feat.npy": os.path.join(features_dir, "image_features_resnet18.npy"),
            "text_feat.npy": os.path.join(features_dir, "text_features_minilm.npy"),
            "meta_feat.npy": os.path.join(features_dir, "metadata_features.npy"),
            "final_emb.npy": os.path.join(features_dir, "final_gnn_embeddings.npy"),
            "gnn_model.pth": os.path.join(base_dir, "models", "fashion_gnn_model.pth"),
            "mapping.csv": os.path.join(features_dir, "edge_matrix_features", "id_to_idx_mapping.csv")
        }

        for name, src in files_to_save.items():
            if os.path.exists(src):
                shutil.copy(src, os.path.join(v_dir, name))

        # Đăng ký vào bảng model_versions (có thể dùng SQLAlchemy để insert)
        print(f"Đã lưu trữ phiên bản: {version_id} tại {v_dir}")
        return version_id