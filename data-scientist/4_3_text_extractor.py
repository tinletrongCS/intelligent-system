import pandas as pd
import numpy as np
import os
import torch
from sentence_transformers import SentenceTransformer
from tqdm import tqdm

preprocessed_csv = r"E:\Hcmut material\AI\Intelligence System\intelligent-system\data-scientist\standard_dataset\fashion_preprocessed_dataset.csv"
image_features_ids_csv = r"E:\Hcmut material\AI\Intelligence System\intelligent-system\data-scientist\features\image_features\image_feature_ids.csv"
output_path = r"E:\Hcmut material\AI\Intelligence System\intelligent-system\data-scientist\features\text_features"

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Đang sử dụng thiết bị: {device}")

def extract_text_features():
    global output_path
    print("--- Bắt đầu trích xuất Text Embeddings ---")
    
    # 1. Nạp dữ liệu và Đồng bộ hóa ID
    df_clean = pd.read_csv(preprocessed_csv)
    df_ids = pd.read_csv(image_features_ids_csv)
    
    df_clean['id'] = df_clean['id'].astype(str)
    df_ids['id'] = df_ids['id'].astype(str)
    
    df_final = pd.merge(df_ids, df_clean, on='id', how='left')
    
    # 2. Chuẩn bị văn bản
    print("Đang gộp văn bản để tạo ngữ cảnh...")
    def combine_text(row):
        name = str(row['productDisplayName']) if row['productDisplayName'] != 'not found' else ""
        brand = str(row['brandName']) if row['brandName'] != 'not found' else ""
        desc = str(row['description']) if row['description'] != 'not found' else ""
        style = str(row['style_note']) if row['style_note'] != 'not found' else ""
        return f"{name} {brand} {desc} {style}".strip()

    sentences = df_final.apply(combine_text, axis=1).tolist()

    # 3. Nạp model SENTENCE-BERT (MiniLM)
    print("Đang nạp model all-MiniLM-L6-v2...")
    model = SentenceTransformer('all-MiniLM-L6-v2', device=device)
    
    # 4. Trích xuất theo batch
    
    print(f"Bắt đầu trích xuất embedding cho {len(sentences)} câu...")
    text_embeddings = model.encode(
        sentences, 
        batch_size=128,                 # Với GPU 4GB, batch_size=64 hoặc 128 là cực kỳ an toàn
        show_progress_bar=True, 
        convert_to_numpy=True
    )

    # 5. Lưu kết quả
    output_path = os.path.join(output_path, "text_features_minilm.npy")
    np.save(output_path, text_embeddings)
    
    print("="*50)
    print(f"HOÀN THÀNH!")
    print(f"Kích thước ma trận Text Feature: {text_embeddings.shape}")
    print(f"Mỗi sản phẩm giờ là một vector {text_embeddings.shape[1]} chiều.")
    print(f"File lưu tại: {output_path}")
    print("="*50)

if __name__ == "__main__":
    extract_text_features()