import pandas as pd
import numpy as np
import os
import re
import cv2
from sklearn.preprocessing import LabelEncoder
from bs4 import BeautifulSoup
import nltk
from nltk.corpus import stopwords

# Tải danh sách stopwords
nltk.download('stopwords')
stop_words = set(stopwords.words('english'))

def clean_text(text):
    """Hàm dọn dẹp văn bản chuyên sâu cho Description"""
    if pd.isna(text) or str(text).lower() == 'nan' or text == "":
        return "not found"
    
    try:
        text = text.encode('latin1').decode('utf-8')
    except:
        pass

    # 1. Xóa HTML tags
    text = BeautifulSoup(text, "html.parser").get_text()

    # 2. Xóa ký tự non-ASCII (giun dế Ã?Â)
    text = re.sub(r'[^\x00-\x7F]+', ' ', text)
    
    # 3. Chỉ giữ lại chữ và số
    text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)
    
    # 4. Xóa stopwords và chuẩn hóa
    words = text.lower().split()
    words = [w for w in words if w not in stop_words and len(w) > 1]
    
    result = " ".join(words)
    return result if result != "" else "not found"

def run_preprocessing_pipeline(input_csv, output_csv, image_dir, processed_img_dir):
    print("-Bắt đầu quy trình Tiền xử lý")
    df = pd.read_csv(input_csv)
    
    # Bước 1: Lọc ảnh bị thiếu
    image_files = set([f.split('.')[0] for f in os.listdir(image_dir) if f.endswith(('.jpg', '.png'))])
    df['id_str'] = df['id'].astype(str)
    df = df[df['id_str'].isin(image_files)]
    print(f"1. Đã lọc ảnh. Còn lại: {len(df)} dòng.")

    # Bước 2: Xử lý giá trị thiếu
    df['brandName'] = df['brandName'].fillna("not found")
    df['productDisplayName'] = df['productDisplayName'].fillna("not found")
    
    high_null_cols = ['Neck', 'Fit', 'Occasion', 'Fabric']
    df[high_null_cols] = df[high_null_cols].fillna("Unknown")
    
    low_null_cols = ['usage', 'season', 'baseColour']
    for col in low_null_cols:
        df[col] = df[col].fillna(df[col].mode()[0])
    print("2. Đã xử lý giá trị thiếu (Brand/Name -> 'not found').")

    # Bước 3: Lọc trùng lặp mềm
    df['desc_len'] = df['description'].astype(str).str.len()
    df = df.sort_values(by='desc_len', ascending=False)
    df = df.drop_duplicates(subset=['productDisplayName', 'brandName', 'baseColour', 'gender'], keep='first')
    df = df.drop(columns=['desc_len'])
    print(f"3. Đã lọc trùng lặp. Còn lại: {len(df)} dòng.")

    # Bước 4: Tiền xử lý Description và Style Note
    print("4. Đang làm sạch Description...")
    df['description'] = df['description'].apply(clean_text)
    df['style_note']=df['style_note'].apply(clean_text)

    # Bước 5: Mã hóa (Encoding)
    print("5. Đang mã hóa Brand và Product Name...")
    le_brand = LabelEncoder()
    le_name = LabelEncoder()
    le_type = LabelEncoder()
    
    df['brand_label'] = le_brand.fit_transform(df['brandName'].astype(str))
    df['productName_label'] = le_name.fit_transform(df['productDisplayName'].astype(str))
    df['articleType_label'] = le_type.fit_transform(df['articleType'].astype(str))
    
    # One-hot cho các trường định danh thấp
    df = pd.get_dummies(df, columns=['gender', 'usage', 'season'], prefix=['gen', 'use', 'sea'], dtype=int)

    # Bước 6: Numerical Scaling
    df['price_log'] = np.log1p(df['price'])
    df['rating_norm'] = df['myntraRating'] / 5.0

    # Bước 7: Image Prep (Resize) ---
    print("6. Đang xử lý Resize ảnh...")
    # os.makedirs(processed_img_dir, exist_ok=True)
    # count = 0
    # for idx, row in df.iterrows():
    #     img_id = row['id_str']
    #     img_path = os.path.join(image_dir, f"{img_id}.jpg")
    #     img = cv2.imread(img_path)
    #     if img is not None:
    #         img_resized = cv2.resize(img, (224, 224))
    #         cv2.imwrite(os.path.join(processed_img_dir, f"{img_id}.jpg"), img_resized)
        
    #     count += 1
    #     if count % 5000 == 0: print(f"   > Đã xong {count} ảnh...")
            
    df = df.drop(columns=['id_str'])
    df.to_csv(output_csv, index=False, encoding='utf-8-sig')
    print(f"\n -Hoàn thành")
    print(f"Đầu ra: {output_csv}")

raw_csv = r"E:\Hcmut material\AI\Intelligence System\intelligent-system\data-scientist\orignal_dataset\fashion_original_dataset.csv"
output_csv = r"E:\Hcmut material\AI\Intelligence System\intelligent-system\data-scientist\standard_dataset\fashion_preprocessed_dataset.csv"
image_path = r'E:\Hcmut material\AI\Intelligence System\archive\fashion-dataset\images'
processed_img_dir = r'E:\Hcmut material\AI\Intelligence System\archive\fashion-dataset\processed_images'

run_preprocessing_pipeline(raw_csv, output_csv, image_path, processed_img_dir)