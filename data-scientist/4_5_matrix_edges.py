import pandas as pd
import numpy as np
import os
import torch
from itertools import combinations
from tqdm import tqdm

# --- CẤU HÌNH ĐƯỜNG DẪN ---
image_features_ids_csv = r"E:\Hcmut material\AI\Intelligence System\intelligent-system\data-scientist\features\image_features\image_feature_ids.csv"
preprocessed_csv = r"E:\Hcmut material\AI\Intelligence System\intelligent-system\data-scientist\standard_dataset\fashion_preprocessed_dataset.csv"
# Mình đổi tên thành base_dir để tránh nhầm lẫn
base_dir = r"E:\Hcmut material\AI\Intelligence System\intelligent-system\data-scientist\features"

def build_edges():
    print("--- Bắt đầu xây dựng Edges cho Đồ thị ---")
    
    # 1. Nạp dữ liệu và đồng bộ
    if not os.path.exists(preprocessed_csv) or not os.path.exists(image_features_ids_csv):
        print("Lỗi: Không tìm thấy file đầu vào. Kiểm tra lại đường dẫn!")
        return

    df_clean = pd.read_csv(preprocessed_csv)
    df_ids = pd.read_csv(image_features_ids_csv)
    
    df_clean['id'] = df_clean['id'].astype(str)
    df_ids['id'] = df_ids['id'].astype(str)
    
    df_final = pd.merge(df_ids, df_clean, on='id', how='left')
    
    # Mapping từ ID (chuỗi) sang Index (số nguyên 0, 1, 2...)
    id_to_idx = {str(id_val): i for i, id_val in enumerate(df_final['id'])}
    
    edge_list = []

    # 2. Tạo cạnh dựa trên Brand
    print("Đang nối cạnh theo Brand...")
    brand_groups = df_final.groupby('brand_label').indices
    for brand, indices in tqdm(brand_groups.items(), desc="Brand Edges"):
        if len(indices) > 1:
            if len(indices) > 100:
                # Tránh bùng nổ số lượng cạnh với các Brand quá lớn
                for u in indices:
                    neighbors = np.random.choice(indices, 5, replace=False)
                    for v in neighbors:
                        if u != v:
                            edge_list.append([u, v])
            else:
                for u, v in combinations(indices, 2):
                    edge_list.append([u, v])
                    edge_list.append([v, u])

    # 3. Tạo cạnh dựa trên Article Type
    print("Đang nối cạnh theo Article Type...")
    type_groups = df_final.groupby('articleType_label').indices
    for a_type, indices in tqdm(type_groups.items(), desc="Type Edges"):
        if len(indices) > 1:
            for u in indices:
                num_neighbors = min(3, len(indices) - 1)
                neighbors = np.random.choice(indices, num_neighbors, replace=False)
                for v in neighbors:
                    if u != v:
                        edge_list.append([u, v])
                        edge_list.append([v, u])

    # 4. Chuyển thành EDGE_INDEX và loại bỏ trùng lặp
    print("Đang chuẩn hóa Edge Index...")
    edge_index = np.array(edge_list).T
    edge_index = np.unique(edge_index, axis=1)
    
    # 5. LƯU KẾT QUẢ (PHẦN QUAN TRỌNG NHẤT)
    # Tạo thư mục con 'graph_data' để chứa kết quả cho gọn
    graph_dir = os.path.join(base_dir, "graph_data")
    if not os.path.exists(graph_dir):
        os.makedirs(graph_dir)
        print(f"Đã tạo thư mục: {graph_dir}")

    edge_output_path = os.path.join(graph_dir, "edge_index.npy")
    mapping_output_path = os.path.join(graph_dir, "id_to_idx_mapping.csv")

    # Lưu file .npy
    np.save(edge_output_path, edge_index)
    
    # Lưu file .csv mapping
    pd.DataFrame(list(id_to_idx.items()), columns=['id', 'idx']).to_csv(mapping_output_path, index=False)

    print("="*50)
    print(f"HOÀN THÀNH XÂY DỰNG ĐỒ THỊ!")
    print(f"Tổng số Nodes: {len(df_final):,}")
    print(f"Tổng số Edges: {edge_index.shape[1]:,}")
    print(f"File cạnh: {edge_output_path}")
    print(f"File mapping: {mapping_output_path}")
    print("="*50)

if __name__ == "__main__":
    build_edges()