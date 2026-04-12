import pandas as pd
import numpy as np
import os
import torch
from itertools import combinations
from tqdm import tqdm

image_features_ids_csv = r"E:\Hcmut material\AI\Intelligence System\intelligent-system\data-scientist\features\image_features\image_feature_ids.csv"
preprocessed_csv = r"E:\Hcmut material\AI\Intelligence System\intelligent-system\data-scientist\standard_dataset\fashion_preprocessed_dataset.csv"
output_path = r"E:\Hcmut material\AI\Intelligence System\intelligent-system\data-scientist\features"

def build_edges():
    print("--- Bắt đầu xây dựng Edges cho Đồ thị ---")
    
    # 1. Nạp dữ liệu và đồng bộ
    df_clean = pd.read_csv(preprocessed_csv)
    df_ids = pd.read_csv(image_features_ids_csv)
    
    df_clean['id'] = df_clean['id'].astype(str)
    df_ids['id'] = df_ids['id'].astype(str)
    
    df_final = pd.merge(df_ids, df_clean, on='id', how='left')
    
    id_to_idx = {str(id_val): i for i, id_val in enumerate(df_final['id'])}
    
    edge_list = []

    # 2. Tạo cạnh dựa trên brand (thương hiệu))
    print("Đang nối cạnh theo Brand...")
    brand_groups = df_final.groupby('brand_label').indices
    for brand, indices in tqdm(brand_groups.items(), desc="Brand Edges"):
        if len(indices) > 1:
            # Tạo các cặp (u, v) trong cùng 1 brand
            # Lưu ý: Với brand quá lớn (ví dụ Nike có 5000 món), combinations sẽ gây treo máy
            # Giải pháp: Chỉ lấy tối đa 50 cặp ngẫu nhiên cho mỗi node để đồ thị không quá dày
            if len(indices) > 100:
                # Nếu brand quá lớn, ta chỉ nối node với 5 hàng xóm ngẫu nhiên trong brand đó
                for u in indices:
                    neighbors = np.random.choice(indices, 5, replace=False)
                    for v in neighbors:
                        if u != v:
                            edge_list.append([u, v])
            else:
                for u, v in combinations(indices, 2):
                    edge_list.append([u, v])
                    edge_list.append([v, u])

    # 3. Tạo cạnh dựa trên article type (loại sản phẩm)
    print("Đang nối cạnh theo Article Type...")
    type_groups = df_final.groupby('articleType_label').indices
    for a_type, indices in tqdm(type_groups.items(), desc="Type Edges"):
        if len(indices) > 1:
            # Tương tự Brand, giới hạn số cạnh để tránh bùng nổ bộ nhớ
            for u in indices:
                # Mỗi sản phẩm nối với 3 sản phẩm khác cùng loại
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
    
    # 5. Lưu kết quả
    output_path = os.path.join(output_path, "edge_index.npy")
    np.save(output_path, edge_index)
    
    # Lưu ID mapping để sau này tra cứu ngược từ Index ra ID
    mapping_path = os.path.join(output_path, "id_to_idx_mapping.csv")
    pd.DataFrame(list(id_to_idx.items()), columns=['id', 'idx']).to_csv(mapping_path, index=False)

    print("="*50)
    print(f"HOÀN THÀNH XÂY DỰNG ĐỒ THỊ!")
    print(f"Tổng số Nodes: {len(df_final):,}")
    print(f"Tổng số Edges: {edge_index.shape[1]:,}")
    print(f"Mật độ đồ thị: {edge_index.shape[1]/len(df_final):.2f} cạnh/node")
    print(f"File cạnh lưu tại: {output_path}")
    print("="*50)

if __name__ == "__main__":
    build_edges()