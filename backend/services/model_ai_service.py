import os
import sys
import shutil
import requests
import pandas as pd
from pathlib import Path
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import desc

base_dir = Path(__file__).resolve().parent.parent.parent
ai_code_path = base_dir / "data_scientist"

if str(base_dir) not in sys.path:
    sys.path.append(str(base_dir))

from data_scientist.eda_original_1 import OriginalDatasetEDA
from data_scientist.preprocessing_2 import FashionPreprocessor
from data_scientist.eda_normalized_3 import NormalizedDatasetEDA
from data_scientist.image_extractor_4_1 import ImageFeatureExtractor
from data_scientist.metadata_extractor_4_2 import MetadataFeatureExtractor
from data_scientist.text_extractor_4_3 import TextFeatureExtractor
from data_scientist.feature_fusion_4_4 import FeatureFusion
from data_scientist.edge_builder_4_5 import EdgeBuilder
from data_scientist.train_GNN_4_6 import GNNTrainer
from repositories import product_repository
from models.model_ai_model import ModelVersion, EDAReport

class AIPipelineOrchestrator:
    def __init__(self, db: Session):
        self.db = db
        
        self.original_data_dir = ai_code_path / "orignal_dataset"
        self.standard_data_dir = ai_code_path / "standard_dataset"
        self.features_dir = ai_code_path / "features"
        self.reports_dir = ai_code_path / "reports"
        self.raw_images_dir = ai_code_path / "images" 
        self.models_dir = ai_code_path / "models"
        
        self.source_images_dir = Path(r"E:\Hcmut material\AI\Intelligence System\fashion-dataset\images")

        for folder in [self.original_data_dir, self.standard_data_dir, 
                       self.features_dir, self.reports_dir, 
                       self.raw_images_dir, self.models_dir]:
            folder.mkdir(parents=True, exist_ok=True)


    def _get_relative_path(self, absolute_path: Path) -> str:
        """Chuyển đổi Path tuyệt đối thành string tương đối so với BASE_DIR"""
        try:
            return str(absolute_path.relative_to(base_dir))
        except ValueError:
            return str(absolute_path)


    def download_product_images(self, products):
        print(f"1. Đang đồng bộ ảnh từ thư mục nguồn: {self.source_images_dir.name}")
        count = 0
        missing_count = 0
        for p in products:
            if not p.image_url: continue
            source_file = self.source_images_dir / f"{p.image_url}.jpg"
            save_path = self.raw_images_dir / f"{p.id}.jpg"
            if not save_path.exists():
                if source_file.exists():
                    try:
                        shutil.copy(str(source_file), str(save_path))
                        count += 1
                    except Exception: pass
                else: missing_count += 1


    def sync_db_to_ai_input(self):
        print("2. Đồng bộ hóa dữ liệu Database sang CSV")
        products = product_repository.get_all_products(self.db, limit=100000)
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
            "masterCategory": p.master_category, 
            "subCategory": p.sub_category, 
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


    def check_incremental(self, current_count):
        last_version = self.db.query(ModelVersion).filter(ModelVersion.is_active == True).order_by(desc(ModelVersion.created_at)).first()

        if not last_version:
            return True

        return current_count > last_version.product_count


    def execute_ai_domino(self, version_tag, db_model_id):
        """Thực thi chuỗi Class AI (Domino)"""
        print(f"3. Thực thi Domino AI: {version_tag} ---")
        
        # EDA Original
        out_orig = self.reports_dir / version_tag / "original"
        OriginalDatasetEDA(input_path=str(self.original_data_dir / "fashion_original_dataset.csv"),
                           output_dir=str(out_orig), image_dir=str(self.raw_images_dir)).run_all()
        self._save_eda_to_db(db_model_id, "original", out_orig)

        # Preprocessing
        FashionPreprocessor(input_csv=str(self.original_data_dir / "fashion_original_dataset.csv"),
                            output_csv=str(self.standard_data_dir / "fashion_preprocessed_dataset.csv"),
                            image_dir=str(self.raw_images_dir)).run_all()

        # EDA Normalized
        out_norm = self.reports_dir / version_tag / "normalized"
        NormalizedDatasetEDA(standard_csv=str(self.standard_data_dir / "fashion_preprocessed_dataset.csv"),
                             original_csv=str(self.original_data_dir / "fashion_original_dataset.csv"),
                             output_dir=str(out_norm)).run_all()
        self._save_eda_to_db(db_model_id, "normalized", out_norm)

        # Extractors
        ImageFeatureExtractor(input_csv=str(self.standard_data_dir / "fashion_preprocessed_dataset.csv"),
                              output_dir=str(self.features_dir / "image_features"),
                              image_dir=str(self.raw_images_dir)).run_extraction()
        
        MetadataFeatureExtractor(input_csv=str(self.standard_data_dir / "fashion_preprocessed_dataset.csv"),
                                 id_csv=str(self.features_dir / "image_features" / "image_feature_ids.csv"),
                                 output_dir=str(self.features_dir / "metadata_features")).run_extraction()

        TextFeatureExtractor(input_csv=str(self.standard_data_dir / "fashion_preprocessed_dataset.csv"),
                             id_csv=str(self.features_dir / "image_features" / "image_feature_ids.csv"),
                             output_dir=str(self.features_dir / "text_features")).run_extraction()

        # Fusion & EdgeBuilder
        FeatureFusion(visual_path=str(self.features_dir / "image_features" / "image_features_resnet18.npy"),
                      text_path=str(self.features_dir / "text_features" / "text_features.npy"),
                      meta_path=str(self.features_dir / "metadata_features" / "metadata_features.npy"),
                      output_dir=str(self.features_dir / "final_node_features")).run_fusion()

        EdgeBuilder(input_csv=str(self.standard_data_dir / "fashion_preprocessed_dataset.csv"),
                    id_csv=str(self.features_dir / "image_features" / "image_feature_ids.csv"),
                    output_dir=str(self.features_dir / "graph_data")).run_build()

        # GNN Training
        last_ver = self.db.query(ModelVersion).order_by(desc(ModelVersion.created_at)).first()
        trainer = GNNTrainer(node_feat_path=str(self.features_dir / "final_node_features" / "final_node_features.npy"),
                             edge_index_path=str(self.features_dir / "graph_data" / "edge_index.npy"),
                             output_dir=str(self.features_dir / "models"))
        trainer.run_training(last_model_path=last_ver.model_weights_path if last_ver else None)


    def _save_eda_to_db(self, model_id, eda_type, report_dir: Path):
        """Lưu đường dẫn báo cáo EDA vào DB bằng đường dẫn tương đối"""
        report = EDAReport(
            version_id=model_id,
            eda_type=eda_type,
            data_profiling_txt=self._get_relative_path(report_dir / "1_data_profiling.txt"),
            missing_value_plot=self._get_relative_path(report_dir / "2_missing_value_analysis.png"),
            category_distribution_plot=self._get_relative_path(report_dir / "3_category_distribution.png")
        )
        self.db.add(report)
        self.db.commit()


    def archive_current_version(self, current_count):
        v_tag = f"v_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        v_dir = self.models_dir / v_tag
        v_dir.mkdir(parents=True, exist_ok=True)

        # File gốc cần copy
        files_map = {
            "image_feat.npy": self.features_dir / "image_features" / "image_features_resnet18.npy",
            "text_feat.npy": self.features_dir / "text_features" / "text_features.npy",
            "meta_feat.npy": self.features_dir / "metadata_features" / "metadata_features.npy",
            "final_emb.npy": self.features_dir / "models" / "final_gnn_embeddings.npy",
            "gnn_weights.pth": self.features_dir / "models" / "fashion_gnn_model.pth"
        }

        for name, src in files_map.items():
            if src.exists(): shutil.copy(str(src), str(v_dir / name))

        new_version = ModelVersion(
            version_tag=v_tag,
            image_feat_path=self._get_relative_path(v_dir / "image_feat.npy"),
            gnn_emb_path=self._get_relative_path(v_dir / "final_emb.npy"),
            model_weights_path=self._get_relative_path(v_dir / "gnn_weights.pth"),
            text_feat_path=self._get_relative_path(v_dir / "text_feat.npy"),
            meta_feat_path=self._get_relative_path(v_dir / "meta_feat.npy"),
            product_count=current_count,
            is_active=True
        )
        self.db.query(ModelVersion).update({ModelVersion.is_active: False})
        self.db.add(new_version)
        self.db.commit()
        self.db.refresh(new_version)
        
        return v_tag, new_version


    async def run_full_pipeline(self):
        """Hàm điều phối tổng lực - Đã sửa lỗi thứ tự Archive"""
        try:
            print("=== BẮT ĐẦU CHẠY PIPELINE TỔNG LỰC ===")
            
            # Bước 1: Lấy dữ liệu sản phẩm
            prods = product_repository.get_all_products(self.db, limit=100000)
            
            # Bước 2: Đồng bộ dữ liệu sang CSV và lấy count thực tế từ file
            # Khải nên lấy count ở đây cho chuẩn nhất
            actual_count, _ = self.sync_db_to_ai_input()
            
            # Bước 3: Kiểm tra tăng trưởng (Dùng count thực tế)
            if not self.check_incremental(actual_count):
                return None

            # Bước 4: Đồng bộ ảnh
            self.download_product_images(prods)
            
            # Bước 5: Chạy chuỗi Domino AI TRƯỚC
            # Tạo một version tag tạm để đặt tên folder báo cáo EDA
            v_tag_temp = f"v_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Tạo một bản ghi ModelVersion "nháp" để lấy ID truyền vào Domino
            # Hoặc ông có thể truyền v_tag_temp vào trước
            print("--- [DOMINO] Bắt đầu huấn luyện AI ---")
            
            # QUAN TRỌNG: Chạy Domino để sinh ra file .npy và .pth MỚI NHẤT
            # Vì execute_ai_domino của ông cần db_model_id, ta sẽ tạo ModelVersion trước 
            # nhưng chưa copy file vội
            new_version = ModelVersion(
                version_tag=v_tag_temp,
                product_count=actual_count,
                is_active=False # Chưa active vì chưa train xong
            )
            self.db.add(new_version)
            self.db.commit()
            self.db.refresh(new_version)

            # Thực thi domino
            self.execute_ai_domino(v_tag_temp, new_version.id)
            
            # Bước 6: Sau khi train xong, mới "Đóng gói" (Archive) file vào folder version
            print(f"--- [ARCHIVE] Đang đóng gói file cho phiên bản {v_tag_temp} ---")
            self.finalize_version_archive(v_tag_temp, new_version)
            
            print(f"=== PIPELINE HOÀN TẤT THÀNH CÔNG: {v_tag_temp} ===")
            return v_tag_temp

        except Exception as e:
            self.db.rollback()
            print(f"--- [FATAL ERROR] Pipeline sụp đổ: {str(e)} ---")
            raise e

    def finalize_version_archive(self, v_tag, version_obj):
        """Hàm phụ trợ để copy file sau khi train xong và update đường dẫn"""
        v_dir = self.models_dir / v_tag
        v_dir.mkdir(parents=True, exist_ok=True)

        files_map = {
            "image_feat.npy": self.features_dir / "image_features" / "image_features_resnet18.npy",
            "text_feat.npy": self.features_dir / "text_features" / "text_features.npy",
            "meta_feat.npy": self.features_dir / "metadata_features" / "metadata_features.npy",
            "final_emb.npy": self.features_dir / "models" / "final_gnn_embeddings.npy",
            "gnn_weights.pth": self.features_dir / "models" / "fashion_gnn_model.pth"
        }

        for name, src in files_map.items():
            if src.exists():
                shutil.copy(str(src), str(v_dir / name))

        # Cập nhật đường dẫn vào bản ghi đã tạo
        version_obj.image_feat_path = self._get_relative_path(v_dir / "image_feat.npy")
        version_obj.gnn_emb_path = self._get_relative_path(v_dir / "final_emb.npy")
        version_obj.model_weights_path = self._get_relative_path(v_dir / "gnn_weights.pth")
        version_obj.text_feat_path = self._get_relative_path(v_dir / "text_feat.npy")
        version_obj.meta_feat_path = self._get_relative_path(v_dir / "meta_feat.npy")
        version_obj.is_active = True # Kích hoạt bản này lên

        # Tắt các bản cũ
        self.db.query(ModelVersion).filter(ModelVersion.id != version_obj.id).update({ModelVersion.is_active: False})
        self.db.commit()