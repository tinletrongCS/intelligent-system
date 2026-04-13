import os
import sys
import shutil
import requests
import pandas as pd
from pathlib import Path
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import desc
from repositories import product_repository
from models.model_ai_model import ModelVersion, EDAReport

from data_scientist.eda_original_1 import OriginalDatasetEDA
from data_scientist.preprocessing_2 import FashionPreprocessor
from data_scientist.eda_normalized_3 import NormalizedDatasetEDA
from data_scientist.image_extractor_4_1 import ImageFeatureExtractor
from data_scientist.metadata_extractor_4_2 import MetadataFeatureExtractor
from data_scientist.text_extractor_4_3 import TextFeatureExtractor
from data_scientist.feature_fusion_4_4 import FeatureFusion
from data_scientist.edge_builder_4_5 import EdgeBuilder
from data_scientist.train_GNN_4_6 import GNNTrainer


base_dir = Path(__file__).resolve().parent.parent.parent
ai_code_path = base_dir / "data-scientist"

if str(base_dir) not in sys.path:
    sys.path.append(str(base_dir))

class AIPipelineOrchestrator:
    def __init__(self, db: Session):
        self.db = db
        # Định nghĩa các thư mục dữ liệu tương đối
        self.original_data_dir = ai_code_path / "orignal_dataset"
        self.standard_data_dir = ai_code_path / "standard_dataset"
        self.features_dir = ai_code_path / "features"
        self.reports_dir = ai_code_path / "reports"
        self.raw_images_dir = ai_code_path / "images" 
        self.raw_images_dir.mkdir(parents=True, exist_ok=True)
        
        # Tự động tạo thư mục nếu chưa có
        for folder in [self.original_data_dir, self.standard_data_dir, self.features_dir, self.reports_dir]:
            folder.mkdir(parents=True, exist_ok=True)

    def download_product_images(self, products):
        """
        Duyệt qua danh sách sản phẩm và tải ảnh về nếu chưa tồn tại cục bộ.
        """
        print("--- Đang nạp ảnh từ URL vào thư mục cục bộ ---")
        count = 0
        for p in products:
            if not p.image_url:
                continue
            
            # Đặt tên file theo ID sản phẩm để đồng bộ với extractor
            file_extension = p.image_url.split('.')[-1].split('?')[0]
            if file_extension.lower() not in ['jpg', 'jpeg', 'png']:
                file_extension = 'jpg'
                
            img_filename = f"{p.id}.{file_extension}"
            save_path = self.raw_images_dir / img_filename

            # Kiểm tra nếu ảnh chưa tồn tại thì mới tải (tránh tải lại ảnh cũ)
            if not save_path.exists():
                try:
                    response = requests.get(p.image_url, timeout=10)
                    if response.status_code == 200:
                        with open(save_path, 'wb') as f:
                            f.write(response.content)
                        count += 1
                except Exception as e:
                    print(f"Lỗi tải ảnh ID {p.id}: {e}")
            
            if count % 100 == 0 and count > 0:
                print(f"   > Đã tải thêm {count} ảnh mới...")
        
        print(f"--- Hoàn tất nạp ảnh. Tổng số ảnh hiện có: {len(list(self.raw_images_dir.glob('*.jpg')))}")

    def sync_db_to_ai_input(self):
        """Lấy dữ liệu và lưu vào folder tương đối"""
        products = product_repository.get_all_products(self.db, limit=100000)
        
        # Map dữ liệu linh hoạt (đảm bảo đủ trường cho Preprocessing)
        data = [{
            "id": str(p.id),
            "brandName": p.brand_name,
            "productDisplayName": p.product_display_name,
            "description": p.description,
            "style_note": p.style_note,
            "price": p.price,
            "discountedPrice": p.discounted_price,
            "articleType": p.article_type,
            "gender": p.gender,
            "season": p.season,
            "usage": p.usage,
            "myntraRating": p.myntra_rating or 0.0,
            "baseColour": p.base_colour,
            "fabric": p.fabric,
            "fit": p.fit,
            "neck": p.neck,
            "occasion": p.occasion
        } for p in products]
        
        csv_path = self.original_data_dir / "fashion_original_dataset.csv"
        pd.DataFrame(data).to_csv(csv_path, index=False)
        return len(data), str(csv_path)

    def execute_ai_domino(self, version_tag, db_model_id):
        """Khởi tạo các Class AI với đường dẫn tương đối"""
        
        # 1. EDA Original
        out_orig = self.reports_dir / version_tag / "original"
        OriginalDatasetEDA(
            input_path=str(self.original_data_dir / "fashion_original_dataset.csv"),
            output_dir=str(out_orig),
            image_dir=str(self.raw_images_dir)
        ).run_all()
        self._save_eda_to_db(db_model_id, "original", out_orig)

        # 2. Preprocessing
        FashionPreprocessor(
            input_csv=str(self.original_data_dir / "fashion_original_dataset.csv"),
            output_csv=str(self.standard_data_dir / "fashion_preprocessed_dataset.csv"),
            image_dir=str(self.raw_images_dir)
        ).run_all()

        # 3. EDA Normalized
        out_norm = self.reports_dir / version_tag / "normalized"
        NormalizedDatasetEDA(
            standard_csv=str(self.standard_data_dir / "fashion_preprocessed_dataset.csv"),
            output_dir=str(out_norm)
        ).run_all()
        self._save_eda_to_db(db_model_id, "normalized", out_norm)

        # 4. Extractors & Fusion
        # (Truyền tham số tương tự để ép các Class dùng folder tương đối)
        ImageFeatureExtractor(
            input_csv=str(self.standard_data_dir / "fashion_preprocessed_dataset.csv"),
            output_dir=str(self.features_dir / "image_features"),
            image_dir=str(self.raw_images_dir)
        ).run_extraction()
        
        MetadataFeatureExtractor(
            input_csv=str(self.standard_data_dir / "fashion_preprocessed_dataset.csv"),
            id_csv=str(self.features_dir / "image_features" / "image_feature_ids.csv"),
            output_dir=str(self.features_dir / "metadata_features")
        ).run_extraction()

        TextFeatureExtractor(
            input_csv=str(self.standard_data_dir / "fashion_preprocessed_dataset.csv"),
            id_csv=str(self.features_dir / "image_features" / "image_feature_ids.csv"),
            output_dir=str(self.features_dir / "text_features")
        ).run_extraction()

        FeatureFusion(
            visual_path=str(self.features_dir / "image_features" / "image_features_resnet18.npy"),
            text_path=str(self.features_dir / "text_features" / "text_features_minilm.npy"),
            meta_path=str(self.features_dir / "metadata_features" / "metadata_features.npy"),
            output_dir=str(self.features_dir / "final_node_features")
        ).run_fusion()

        # 5. Graph & Training
        EdgeBuilder(
            input_csv=str(self.standard_data_dir / "fashion_preprocessed_dataset.csv"),
            id_csv=str(self.features_dir / "image_features" / "image_feature_ids.csv"),
            output_dir=str(self.features_dir / "graph_data")
        ).run_build()

        last_version = self.db.query(ModelVersion).order_by(desc(ModelVersion.created_at)).first()
        trainer = GNNTrainer(
            node_feat_path=str(self.features_dir / "final_node_features" / "final_node_features.npy"),
            edge_index_path=str(self.features_dir / "graph_data" / "edge_index.npy"),
            output_dir=str(self.features_dir / "models")
        )
        trainer.run_training(last_model_path=last_version.model_weights_path if last_version else None)

    def _save_eda_to_db(self, model_id, eda_type, report_dir):
        """Lưu đường dẫn (tương đối) vào DB để dễ quản lý"""
        report = EDAReport(
            version_id=model_id,
            eda_type=eda_type,
            data_profiling_txt=str(report_dir / "1_data_profiling.txt"),
            missing_value_plot=str(report_dir / "2_missing_value_analysis.png"),
            category_distribution_plot=str(report_dir / "3_category_distribution.png")
        )
        self.db.add(report)
        self.db.commit()

    def archive_current_version(self):
        """Lưu trữ trọn bộ đặc trưng vào thư mục Version mới"""
        v_tag = f"v_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        v_dir = os.path.join(self.ai_base_path, "models", "registry", v_tag)
        os.makedirs(v_dir, exist_ok=True)

        # Bản đồ các file cần lưu trữ
        files = {
            "image_feat.npy": os.path.join(self.features_dir, "image_features", "image_features_resnet18.npy"),
            "text_feat.npy": os.path.join(self.features_dir, "text_features", "text_features_minilm.npy"),
            "meta_feat.npy": os.path.join(self.features_dir, "metadata_features", "metadata_features.npy"),
            "final_emb.npy": os.path.join(self.features_dir, "models", "final_gnn_embeddings", "final_gnn_embeddings.npy"),
            "gnn_weights.pth": os.path.join(self.features_dir, "models", "fashion_gnn_model.pth")
        }

        for name, src in files.items():
            if os.path.exists(src):
                shutil.copy(src, os.path.join(v_dir, name))

        # Đăng ký vào bảng ModelVersion
        new_version = ModelVersion(
            version_tag=v_tag,
            image_feat_path=os.path.join(v_dir, "image_feat.npy"),
            gnn_emb_path=os.path.join(v_dir, "final_emb.npy"),
            model_weights_path=os.path.join(v_dir, "gnn_weights.pth"),
            is_active=True
        )
        # Tắt các version cũ
        self.db.query(ModelVersion).update({ModelVersion.is_active: False})
        
        self.db.add(new_version)
        self.db.commit()
        self.db.refresh(new_version)
        return v_tag, new_version.id

    async def run_full_pipeline(self):
        """Hàm main điều phối toàn bộ quy trình"""
        try:
            products = product_repository.get_all_products(self.db, limit=100000)
            
            self.download_product_images(products)

            count, _ = self.sync_db_to_ai_input()
            
            if self.check_incremental(count):
                print(f"--- Bắt đầu quy trình huấn luyện phiên bản mới ---")
                # 1. Tạo bản lưu trữ vật lý và bản ghi DB trước
                v_tag, model_db_id = self.archive_current_version()
                
                # 2. Thực thi chuỗi Domino AI
                self.execute_ai_domino(v_tag, model_db_id)
                
                print(f"--- Pipeline hoàn tất thành công: {v_tag} ---")
                return v_tag
            else:
                print("Dữ liệu không thay đổi. Bỏ qua.")
                return None
        except Exception as e:
            self.db.rollback()
            print(f"Lỗi Pipeline: {str(e)}")
            raise e