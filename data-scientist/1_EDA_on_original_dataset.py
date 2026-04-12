import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from wordcloud import WordCloud
import os
import io
import sys

# Cấu hình thư mục đầu ra
output_dir = r"E:\Hcmut material\AI\Intelligence System\intelligent-system\data-scientist\orignal_dataset\eda_results"
os.makedirs(output_dir, exist_ok=True)

def save_text_report(task_name, content):
    """Hỗ trợ lưu nội dung văn bản vào file .txt"""
    file_path = os.path.join(output_dir, f"{task_name}.txt")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

# 1. Load data
try:
    df = pd.read_csv(r'E:\Hcmut material\AI\Intelligence System\intelligent-system\data-scientist\orignal_dataset\fashion_original_dataset.csv')
    print("Dữ liệu đã được load thành công.")
except FileNotFoundError:
    print("Không tìm thấy file. Vui lòng kiểm tra lại đường dẫn!")
    sys.exit()

# Bước 1: Kiểm định schema và kiểu dữ liệu
def data_profiling_1():
    task_name = "1_data_profiling"
    print(f"Đang thực hiện {task_name}...")
    
    buffer = io.StringIO()
    df.info(buf=buffer)
    info_str = buffer.getvalue()
    
    report = []
    report.append("="*50 + "\n1. DATA PROFILING\n" + "="*50)
    report.append("\n[INFO]\n" + info_str)
    report.append("\n[DESCRIBE]\n" + df.describe().to_string())
    
    categorical_cols = ['gender', 'masterCategory', 'subCategory', 'season', 'usage']
    report.append("\n[UNIQUE VALUES]")
    for col in categorical_cols:
        if col in df.columns:
            report.append(f"- {col}: {df[col].nunique()} giá trị")
            
    save_text_report(task_name, "\n".join(report))

# Bước 2: Phân tích các giá trị thiếu (Missing value analysis)
def missing_value_analysis_2():
    task_name = "2_missing_value_analysis"
    print(f"Đang thực hiện {task_name}...")
    
    null_counts = df.isnull().sum()
    null_percentages = (df.isnull().sum() / len(df)) * 100
    missing_data = pd.DataFrame({
        'Total Null': null_counts,
        'Percentage (%)': null_percentages
    }).sort_values(by='Percentage (%)', ascending=False)

    # Lưu text
    save_text_report(task_name, missing_data.to_string())

    # Lưu ảnh
    plt.figure(figsize=(12, 6))
    sns.barplot(x=missing_data.index, y=missing_data['Percentage (%)'], hue=missing_data.index, palette='viridis', legend=False)
    plt.xticks(rotation=45, ha='right')
    plt.title('Tỷ lệ % dữ liệu bị thiếu')
    plt.savefig(os.path.join(output_dir, f"{task_name}.png"), dpi=300, bbox_inches='tight')
    plt.close()

# Bước 3: Category Distribution
def category_distribution_3():
    task_name = "3_category_distribution"
    print(f"Đang thực hiện {task_name}...")
    
    fig, axes = plt.subplots(1, 3, figsize=(20, 6))
    sns.countplot(data=df, y='masterCategory', hue='masterCategory', ax=axes[0], palette='magma', legend=False, order=df['masterCategory'].value_counts().index)
    
    top_sub = df['subCategory'].value_counts().nlargest(10).index
    sns.countplot(data=df, y='subCategory', hue='subCategory', ax=axes[1], palette='viridis', legend=False, order=top_sub)
    
    sns.countplot(data=df, x='gender', hue='gender', ax=axes[2], palette='coolwarm', legend=False)
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, f"{task_name}_counts.png"), dpi=300)
    plt.close()

    # Heatmap
    plt.figure(figsize=(10, 6))
    usage_season = pd.crosstab(df['usage'], df['season'])
    sns.heatmap(usage_season, annot=True, fmt='d', cmap='YlGnBu')
    plt.savefig(os.path.join(output_dir, f"{task_name}_heatmap.png"), dpi=300)
    plt.close()


# Bước 4 Kiểm tra sự đa dạng của thuộc tính
def attribute_variance_4():
    task_name = "4_attribute_variance"
    print(f"Đang thực hiện {task_name}...")
    
    deep_attrs = ['Fabric', 'Fit', 'Neck', 'Occasion']
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    axes = axes.flatten()

    for i, col in enumerate(deep_attrs):
        if col in df.columns:
            top_vals = df[col].value_counts().nlargest(10)
            sns.barplot(x=top_vals.values, y=top_vals.index, hue=top_vals.index, ax=axes[i], palette='rocket', legend=False)
            axes[i].set_title(f'Top 10: {col}')

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, f"{task_name}.png"), dpi=300)
    plt.close()

# Bước 5: Phân tích chiến lược giá
def price_discount_analysis_5():
    task_name = "5_price_analysis"
    print(f"Đang thực hiện {task_name}...")
    
    df['discount_pct'] = ((df['price'] - df['discountedPrice']) / (df['price'] + 0.001)) * 100

    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    sns.histplot(df['price'], bins=50, kde=True, ax=axes[0], color='blue')
    sns.histplot(df['discount_pct'], bins=30, kde=True, ax=axes[1], color='green')
    plt.savefig(os.path.join(output_dir, f"{task_name}_dist.png"), dpi=300)
    plt.close()

    plt.figure(figsize=(10, 5))
    sns.boxplot(x=df['price'], color='cyan')
    plt.savefig(os.path.join(output_dir, f"{task_name}_boxplot.png"), dpi=300)
    plt.close()

# Bước 6: Đánh giá độ tin cậy của rating
def ratting_insights_6():
    task_name = "6_rating_insights"
    print(f"Đang thực hiện {task_name}...")
    
    plt.figure(figsize=(8, 5))
    sns.countplot(x='myntraRating', data=df, hue='myntraRating', palette='viridis', legend=False)
    plt.savefig(os.path.join(output_dir, f"{task_name}.png"), dpi=300)
    plt.close()

    zero_rating_pct = (df['myntraRating'] == 0).sum() / len(df) * 100
    save_text_report(task_name, f"Tỷ lệ sản phẩm có Rating = 0: {zero_rating_pct:.2f}%")

# Bước 7: Tẽt semantic EDA
def text_semantic_eda_7():
    task_name = "7_text_semantic"
    print(f"Đang thực hiện {task_name}...")
    
    df['style_note_len'] = df['style_note'].str.split().str.len().fillna(0).astype(int)
    df['desc_len'] = df['description'].str.split().str.len().fillna(0).astype(int)

    plt.figure(figsize=(16, 6))
    plt.subplot(1, 2, 1)
    sns.histplot(df['style_note_len'], bins=30, color='purple')
    plt.subplot(1, 2, 2)
    sns.histplot(df['desc_len'], bins=30, color='orange')
    plt.savefig(os.path.join(output_dir, f"{task_name}_len.png"), dpi=300)
    plt.close()

    all_names_list = df['productDisplayName'].dropna().astype(str).tolist()
    all_names = " ".join(all_names_list)
    if all_names.strip():
        wordcloud = WordCloud(width=800, height=400, background_color='white').generate(all_names)
        wordcloud.to_file(os.path.join(output_dir, f"{task_name}_wordcloud.png"))

# Bước 8: Phân tích mối quan hệ thương hiệu (brand dominace)---
def brand_dominance_analysis_8():
    task_name = "8_brand_dominance"
    print(f"Đang thực hiện {task_name}...")
    
    top_brands = df['brandName'].value_counts().nlargest(20)
    plt.figure(figsize=(12, 8))
    sns.barplot(x=top_brands.values, y=top_brands.index, hue=top_brands.index, palette='Spectral', legend=False)
    plt.savefig(os.path.join(output_dir, f"{task_name}.png"), dpi=300, bbox_inches='tight')
    plt.close()

    report = [
        f"Tổng số thương hiệu: {df['brandName'].nunique()}",
        f"Thương hiệu 1 sản phẩm: {(df['brandName'].value_counts() == 1).sum()}"
    ]
    save_text_report(task_name, "\n".join(report))

# Bước 9: Kiểm tra tính nhất quán giữa ảnh và metadata
def image_metadata_consistency_9():
    task_name = "9_consistency_check"
    print(f"Đang thực hiện {task_name}...")
    
    image_dir = r"E:\Hcmut material\AI\Intelligence System\archive\fashion-dataset\images" 
    if not os.path.exists(image_dir):
        save_text_report(task_name, "Lỗi: Thư mục ảnh không tồn tại.")
        return

    image_files = set([f.split('.')[0] for f in os.listdir(image_dir) if f.endswith(('.jpg', '.png'))])
    csv_ids = set(df['id'].astype(str))

    report = [
        f"Số sản phẩm trong CSV: {len(csv_ids)}",
        f"Số file ảnh: {len(image_files)}",
        f"Thiếu ảnh: {len(csv_ids - image_files)}",
        f"Ảnh dư (Orphan): {len(image_files - csv_ids)}"
    ]
    save_text_report(task_name, "\n".join(report))

# Bước 10: Phân tích trùng lặp mềm (soft duplicate check)
def soft_duplicate_10():
    task_name = "10_duplicate_check"
    print(f"Đang thực hiện {task_name}...")
    
    soft_duplicates = df[df.duplicated(subset=['productDisplayName', 'gender', 'baseColour'], keep=False)]
    
    report = [
        f"Nghi ngờ trùng lặp mềm: {len(soft_duplicates)}",
        f"Trùng lặp ID tuyệt đối: {df.duplicated(subset=['id']).sum()}"
    ]
    save_text_report(task_name, "\n".join(report))

if __name__ == "__main__":
    data_profiling_1()
    missing_value_analysis_2()
    category_distribution_3()
    attribute_variance_4()
    price_discount_analysis_5()
    ratting_insights_6()
    text_semantic_eda_7()
    brand_dominance_analysis_8()
    image_metadata_consistency_9()
    soft_duplicate_10()