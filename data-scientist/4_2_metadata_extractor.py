import pandas as pd
import numpy as np
import os

preprocessed_csv = r"E:\Hcmut material\AI\Intelligence System\intelligent-system\data-scientist\standard_dataset\fashion_preprocessed_dataset.csv"
image_features_ids_csv = r"E:\Hcmut material\AI\Intelligence System\intelligent-system\data-scientist\features\image_features\image_feature_ids.csv"
output_path = r"E:\Hcmut material\AI\Intelligence System\intelligent-system\data-scientist\features\metadata_features"

def extract_metadata_features():
    print("--- Bắt đầu trích xuất Metadata Features ---")
    global output_path
    
    # 1. Nạp dữ liệu
    df_clean = pd.read_csv(preprocessed_csv)
    df_ids = pd.read_csv(image_features_ids_csv)
    
    df_clean['id'] = df_clean['id'].astype(str)
    df_ids['id'] = df_ids['id'].astype(str)

    # 2. Đồng bộ hóa: Chỉ lấy những dòng có ID nằm trong danh sách đã trích xuất ảnh
    df_final = pd.merge(df_ids, df_clean, on='id', how='left')
    
    print(f"Tổng số sản phẩm khớp với dữ liệu ảnh: {len(df_final)}")

    # 3. Lựa chọn các đặc trưng
    # Nhóm 1: Đặc trưng số (Numerical)
    num_features = ['price_log', 'rating_norm']
    
    # Nhóm 2: Đặc trưng phân loại đã One-hot (Categorical - Binary)
    one_hot_features = [col for col in df_final.columns if col.startswith(('gen_', 'use_', 'sea_'))]
    
    # Nhóm 3: Đặc trưng nhãn (Label - Cần cân nhắc)
    label_features = ['brand_label', 'articleType_label']

    # Tổng hợp danh sách cột muốn đưa vào vector metadata
    selected_cols = num_features + one_hot_features + label_features
    
    print(f"Các cột được chọn làm metadata: {selected_cols}")
    
    # 4. Trích xuất thành ma trận
    metadata_matrix = df_final[selected_cols].values.astype(np.float32)
    
    output_path = os.path.join(output_path, "metadata_features.npy")
    np.save(output_path, metadata_matrix)
    
    print("="*50)
    print(f"HOÀN THÀNH!")
    print(f"Kích thước ma trận Metadata: {metadata_matrix.shape}")
    print(f"Mỗi sản phẩm giờ là một vector {metadata_matrix.shape[1]} chiều.")
    print(f"File lưu tại: {output_path}")
    print("="*50)

if __name__ == "__main__":
    extract_metadata_features()