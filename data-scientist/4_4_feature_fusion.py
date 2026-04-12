import numpy as np
import os

output_path = r"E:\Hcmut material\AI\Intelligence System\intelligent-system\data-scientist\features\final_node_features"

def fuse_features():
    print("--- Đang hợp nhất các đặc trưng ---")
    
    # 1. Nạp các file .npy
    visual_feat = np.load(r"E:\Hcmut material\AI\Intelligence System\intelligent-system\data-scientist\features\image_features\image_features_resnet18.npy")
    text_feat = np.load(r"E:\Hcmut material\AI\Intelligence System\intelligent-system\data-scientist\features\text_features\text_features_minilm.npy")
    meta_feat = np.load(r"E:\Hcmut material\AI\Intelligence System\intelligent-system\data-scientist\features\metadata_features\metadata_features.npy")
    
    print(f"Kích thước Visual: {visual_feat.shape}")
    print(f"Kích thước Text:   {text_feat.shape}")
    print(f"Kích thước Meta:   {meta_feat.shape}")
    
    # 2. Hợp nhất (Concatenation)
    # Nối theo trục 1 (chiều ngang)
    final_features = np.concatenate([visual_feat, text_feat, meta_feat], axis=1)
    
    # 3. Chuẩn hóa cuối cùng (L2 Normalization)
    norms = np.linalg.norm(final_features, axis=1, keepdims=True)
    norms[norms == 0] = 1
    final_features = final_features / norms
    
    # 4. Lưu ma trận Node Features cuối cùng
    np.save(output_path, final_features.astype(np.float32))
    
    print("="*50)
    print(f"HOÀN THÀNH FEATURE FUSION!")
    print(f"Ma trận Node Features cuối cùng: {final_features.shape}")
    print(f"File lưu tại: {output_path}")
    print("="*50)

if __name__ == "__main__":
    fuse_features()