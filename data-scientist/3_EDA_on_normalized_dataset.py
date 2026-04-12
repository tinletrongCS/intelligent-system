import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os
from wordcloud import WordCloud

# Cấu hình đường dẫn
standard_csv = r"E:\Hcmut material\AI\Intelligence System\intelligent-system\data-scientist\standard_dataset\fashion_preprocessed_dataset.csv"
original_csv = r"E:\Hcmut material\AI\Intelligence System\intelligent-system\data-scientist\orignal_dataset\fashion_original_dataset.csv"
output_eda = r"E:\Hcmut material\AI\Intelligence System\intelligent-system\data-scientist\standard_dataset\eda_results"
os.makedirs(output_eda, exist_ok=True)

df_clean = pd.read_csv(standard_csv)
df_raw = pd.read_csv(original_csv) # Load lại file cũ để so sánh ở bước 3

# 1. Xác nhận "Zero null"
def verify_zero_null_1():
    task_name = "1_Missing_Value_Verification"
    print(f"Đang thực hiện {task_name}...")
    
    null_summary = df_clean.isnull().sum()
    total_null = null_summary.sum()
    
    with open(os.path.join(output_eda, "1_zero_null_check.txt"), "w", encoding='utf-8') as f:
        f.write(f"Tổng số giá trị Null sau Preprocessing: {total_null}\n")
        f.write(null_summary.to_string())

# 2. Kiểm tra phân phối price sau log transformation
def check_price_distribution_2():
    task_name = "2_price_distribution"
    print(f"Đang thực hiện {task_name}...")

    fig, axes = plt.subplots(1, 2, figsize=(15, 6))
    
    sns.histplot(df_raw['price'], kde=True, ax=axes[0], color='red')
    axes[0].set_title('Phân phối Giá gốc (Skewed)')
    
    sns.histplot(df_clean['price_log'], kde=True, ax=axes[1], color='blue')
    axes[1].set_title('Phân phối Giá sau Log Transformation')
    
    plt.tight_layout()
    
    plt.savefig(os.path.join(output_eda, f"{task_name}_comparison.png"), dpi=300)
    plt.close(fig)

    skew_raw = df_raw['price'].skew()
    skew_clean = df_clean['price_log'].skew()
    
    report_path = os.path.join(output_eda, f"{task_name}_report.txt")
    with open(report_path, "w", encoding='utf-8') as f:
        f.write(f"Skewness gốc (Original): {skew_raw:.2f}\n")
        f.write(f"Skewness sau Log (Processed): {skew_clean:.2f}\n")
        f.write("-" * 50 + "\n")
        if abs(skew_clean) < abs(skew_raw):
            f.write("Nhận xét: Log Transformation đã giảm thành công độ lệch của dữ liệu.\n")
        else:
            f.write("Nhận xét: Cần kiểm tra lại dữ liệu nếu độ lệch không giảm.\n")

# 3. Phân tích tác động của deduplication
def analyze_deduplication_impact_3():
    task_name = "3_deduplication_impact"
    print(f"Đang thực hiện {task_name}...")
    
    raw_count = len(df_raw)
    clean_count = len(df_clean)
    removed_count = raw_count - clean_count
    removed_pct = (removed_count / raw_count) * 100 if raw_count > 0 else 0
    
    raw_cat = df_raw['masterCategory'].value_counts()
    clean_cat = df_clean['masterCategory'].value_counts()
    comparison_df = pd.DataFrame({'Before (Raw)': raw_cat, 'After (Clean)': clean_cat}).fillna(0)
    
    ax = comparison_df.plot(kind='bar', figsize=(12, 6), color=['#A9A9A9', '#FF8C00']) # Gray and DarkOrange
    plt.title('Tác động của việc lọc trùng lên các Master Category', fontsize=14)
    plt.ylabel('Số lượng sản phẩm')
    plt.xlabel('Master Category')
    plt.xticks(rotation=45)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    
    plt.savefig(os.path.join(output_eda, f"{task_name}_comparison.png"), dpi=300, bbox_inches='tight')
    plt.close()

    report_path = os.path.join(output_eda, f"{task_name}_report.txt")
    with open(report_path, "w", encoding='utf-8') as f:
        f.write(f"Số lượng dòng ban đầu (Raw):          {raw_count:,} dòng\n")
        f.write(f"Số lượng dòng sau khi lọc (Clean):     {clean_count:,} dòng\n")
        f.write(f"Tổng số dòng bị loại bỏ:              {removed_count:,} dòng\n")
        f.write(f"Tỷ lệ dữ liệu bị cắt giảm:            {removed_pct:.2f}%\n")
        f.write("-" * 60 + "\n")
        f.write("Chi tiết thay đổi theo Master Category:\n\n")
        f.write(comparison_df.to_string())
        f.write("\n\n" + "-" * 60 + "\n")
        f.write("Ghi chú: Dòng bị loại bỏ bao gồm sản phẩm trùng lặp và sản phẩm thiếu ảnh.\n")

# 4. Kiểm tra sự đa dạng của label encoding
# --- 4. KIỂM TRA SỰ ĐA DẠNG CỦA LABEL ENCODING (CARDINALITY CHECK) ---
def check_label_diversity_4():
    task_name = "4_label_diversity"
    print(f"Đang thực hiện {task_name}...")
    
    label_cols = ['brand_label', 'productName_label', 'articleType_label']
    
    # 1. Tính toán số lượng nhãn duy nhất
    diversity_stats = {}
    for col in label_cols:
        diversity_stats[col] = df_clean[col].nunique()
        
    # 2. Vẽ biểu đồ Top 20 Brand Labels
    plt.figure(figsize=(12, 6))
    top_brands = df_clean['brand_label'].value_counts().nlargest(20)
    
    sns.barplot(
        x=top_brands.index, 
        y=top_brands.values, 
        hue=top_brands.index, 
        palette='magma', 
        legend=False
    )
    plt.title('Phân phối Top 20 Brand Labels (Dấu hiệu Imbalance)', fontsize=14)
    plt.xlabel('Brand Label ID')
    plt.ylabel('Số lượng sản phẩm')
    
    plt.savefig(os.path.join(output_eda, f"{task_name}_plot.png"), dpi=300, bbox_inches='tight')
    plt.close() # Đóng plot để giải phóng RAM

    # 3. Ghi báo cáo chi tiết vào file .txt
    report_path = os.path.join(output_eda, f"{task_name}_report.txt")
    with open(report_path, "w", encoding='utf-8') as f:
        f.write(f"Tổng số sản phẩm trong dataset: {len(df_clean):,}\n\n")
        
        f.write("[THỐNG KÊ NHÃN DUY NHẤT (CARDINALITY)]\n")
        for col, count in diversity_stats.items():
            f.write(f"- {col:20}: {count:,} nhãn duy nhất\n")
            
        f.write("\n[PHÂN PHỐI CHI TIẾT TOP 20 BRANDS]\n")
        f.write(top_brands.to_string())
        
        f.write("\n\n" + "-"*60 + "\n")
        f.write("NHẬN XÉT CHIÊN THUẬT:\n")
        
        name_ratio = diversity_stats['productName_label'] / len(df_clean)
        if name_ratio > 0.8:
            f.write(f"- Cảnh báo: productName_label có độ đa dạng quá cao ({name_ratio*100:.1f}%).\n")
            f.write("  => Lời khuyên: Tránh dùng nhãn này làm đặc trưng Categorical trực tiếp.\n")
            f.write("  => Hãy ưu tiên sử dụng Vector văn bản (Embedding) từ tên sản phẩm.\n")
            
        f.write("- Kiểm tra Brand: Nếu Top 1 brand chiếm tỉ trọng quá lớn, mô hình dễ bị bias.\n")

# 5. Kiểm tra độ thưa thớt của one-hot encoding
def check_onehot_sparsity_5():
    task_name = "5_onehot_sparsity"
    print(f"Đang thực hiện {task_name}...")
    
    onehot_cols = [col for col in df_clean.columns if col.startswith(('gen_', 'use_', 'sea_'))]
    
    if not onehot_cols:
        print("Cảnh báo: Không tìm thấy cột One-hot nào để phân tích.")
        return

    fill_rates = df_clean[onehot_cols].mean() * 100
    sparsity = 100 - fill_rates
    
    sparsity_df = pd.DataFrame({
        'Column': onehot_cols,
        'Fill Rate (%)': fill_rates,
        'Sparsity (%)': sparsity
    }).sort_values(by='Fill Rate (%)', ascending=False)
    
    plt.figure(figsize=(12, 10))
    sns.barplot(
        data=sparsity_df, 
        x='Fill Rate (%)', 
        y='Column', 
        hue='Column',
        palette='viridis', 
        legend=False
    )
    plt.axvline(x=1, color='r', linestyle='--', label='Ngưỡng 1% (Rất thưa)')
    plt.title('Tỉ lệ xuất hiện (Fill Rate) của các nhãn One-hot', fontsize=14)
    plt.xlabel('Tỉ lệ xuất hiện (%)')
    plt.legend()
    
    plt.savefig(os.path.join(output_eda, f"{task_name}_plot.png"), dpi=300, bbox_inches='tight')
    plt.close()

    report_path = os.path.join(output_eda, f"{task_name}_report.txt")
    with open(report_path, "w", encoding='utf-8') as f:
        f.write(f"Tổng số cột One-hot phân tích: {len(onehot_cols)}\n\n")
        
        f.write("[TOP 10 NHÃN PHỔ BIẾN NHẤT (Fill Rate cao)]\n")
        f.write(sparsity_df.head(10).to_string(index=False))
        
        f.write("\n\n[TOP 10 NHÃN THƯA THỚT NHẤT (Fill Rate thấp)]\n")
        f.write(sparsity_df.tail(10).to_string(index=False))
        
        very_sparse = sparsity_df[sparsity_df['Fill Rate (%)'] < 1]
        f.write("\n\n" + "-"*60 + "\n")
        f.write(f"SỐ LƯỢNG NHÃN RẤT THƯA (< 1%): {len(very_sparse)}\n")
        if not very_sparse.empty:
            f.write("Danh sách: " + ", ".join(very_sparse['Column'].tolist()))
            
        f.write("\n\nNHẬN XÉT CHIÊN THUẬT:\n")
        if len(very_sparse) > 0:
            f.write("- Một số nhãn có tỉ lệ xuất hiện cực thấp. Nếu mô hình Underfit, hãy cân nhắc gộp các nhãn này vào nhóm 'Others'.\n")

# 6. Phân tích độ dài văn bản sau khi clean (TEXT SHRINKAGE)
def analyze_text_shrinkage_6():
    task_name = "6_text_shrinkage"
    print(f"Đang thực hiện {task_name}...")

    # 1. Tính toán độ dài từ (word count)
    # Chúng ta bỏ qua các giá trị 'not found' để biểu đồ không bị lệch về 0 quá nhiều
    desc_lengths = df_clean[df_clean['description'] != 'not found']['description'].astype(str).apply(lambda x: len(x.split()))
    style_lengths = df_clean[df_clean['style_note'] != 'not found']['style_note'].astype(str).apply(lambda x: len(x.split()))
    
    # 2. Vẽ biểu đồ (Lưu ý: không dùng plt.show)
    fig, axes = plt.subplots(1, 2, figsize=(15, 6))
    
    sns.histplot(desc_lengths, bins=30, kde=True, ax=axes[0], color='purple')
    axes[0].set_title('Phân bổ độ dài Description (Sau Clean)', fontsize=12)
    axes[0].set_xlabel('Số lượng từ')
    
    sns.histplot(style_lengths, bins=30, kde=True, ax=axes[1], color='orange')
    axes[1].set_title('Phân bổ độ dài Style Note (Sau Clean)', fontsize=12)
    axes[1].set_xlabel('Số lượng từ')
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_eda, f"{task_name}_distribution.png"), dpi=300)
    plt.close(fig)

    # 3. Thống kê chi tiết
    total_records = len(df_clean)
    desc_not_found = (df_clean['description'] == 'not found').sum()
    style_not_found = (df_clean['style_note'] == 'not found').sum()
    
    # 4. Ghi báo cáo .txt
    report_path = os.path.join(output_eda, f"{task_name}_report.txt")
    with open(report_path, "w", encoding='utf-8') as f:
        f.write(f"Tổng số bản ghi xử lý: {total_records:,}\n\n")
        
        f.write("[THỐNG KÊ DESCRIPTION]\n")
        f.write(f"- Số lượng 'not found': {desc_not_found:,} ({desc_not_found/total_records*100:.2f}%)\n")
        if not desc_lengths.empty:
            f.write(f"- Độ dài trung bình:  {desc_lengths.mean():.2f} từ\n")
            f.write(f"- Độ dài lớn nhất:     {desc_lengths.max()} từ\n")
        
        f.write("\n[THỐNG KÊ STYLE NOTE]\n")
        f.write(f"- Số lượng 'not found': {style_not_found:,} ({style_not_found/total_records*100:.2f}%)\n")
        if not style_lengths.empty:
            f.write(f"- Độ dài trung bình:  {style_lengths.mean():.2f} từ\n")
            f.write(f"- Độ dài lớn nhất:     {style_lengths.max()} từ\n")
            
        f.write("\n" + "-"*60 + "\n")
        f.write("NHẬN XÉT CHIẾN THUẬT:\n")
        if desc_lengths.max() > 128:
            f.write("- Cảnh báo: Một số Description khá dài, cân nhắc truncation khi dùng BERT.\n")
        if desc_not_found / total_records > 0.3:
            f.write("- Lưu ý: Tỷ lệ thiếu Description cao, Image Feature sẽ đóng vai trò chủ chốt.\n")

# 7. Ma trận tương quan (FEATURE CORRELATION)
def analyze_correlation_7():
    task_name = "7_Feature_Correlation_Analysis"
    print(f"Đang thực hiện {task_name}...")
    
    # Tính toán độ dài văn bản để đưa vào ma trận tương quan
    df_clean['desc_len'] = df_clean['description'].astype(str).apply(lambda x: 0 if x == 'not found' else len(x.split()))
    
    # Chọn các cột số quan trọng
    num_cols = ['price_log', 'rating_norm', 'brand_label', 'articleType_label', 'desc_len']
    corr_matrix = df_clean[num_cols].corr()
    
    plt.figure(figsize=(10, 8))
    sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', fmt=".2f", linewidths=0.5)
    plt.title('Ma trận tương quan giữa các đặc trưng số')
    plt.savefig(os.path.join(output_eda, "7_correlation_heatmap.png"), dpi=300)
    plt.close()

# 8. WordCloud cho Description "SẠCH"
def generate_clean_wordcloud_8():
    task_name = "8_Clean_WordCloud_For_Description"
    print(f"Đang thực hiện {task_name}...")
    
    # Gộp tất cả description, loại bỏ "not found"
    text = " ".join(df_clean[df_clean['description'] != 'not found']['description'].astype(str))
    
    if text.strip():
        wordcloud = WordCloud(width=800, height=400, background_color='white', 
                              max_words=100, colormap='viridis').generate(text)
        
        plt.figure(figsize=(12, 6))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        plt.title('WordCloud: Từ khóa Description sau khi dọn rác')
        plt.savefig(os.path.join(output_eda, "8_clean_wordcloud.png"), dpi=300)
    else:
        print("Cảnh báo: Không có đủ dữ liệu văn bản để tạo WordCloud.")

# 9. Kiểm tra outliers sau khi scale (BOXPLOT)
def check_post_scaling_outliers_9():
    task_name = "9_Boxplot_Post-Scaling_Check"
    print(f"Đang thực hiện {task_name}...")
    
    plt.figure(figsize=(12, 5))
    plt.subplot(1, 2, 1)
    sns.boxplot(x=df_clean['price_log'], color='cyan')
    plt.title('Boxplot: Price (Log Transformed)')
    
    plt.subplot(1, 2, 2)
    sns.boxplot(x=df_clean['rating_norm'], color='lime')
    plt.title('Boxplot: Rating (Normalized)')
    
    plt.savefig(os.path.join(output_eda, "9_post_scaling_boxplot.png"), dpi=300)
    plt.close()

# 10. Đánh giá tính sẵn sàng cho GNN (GRAPH CONNECTIVITY)
def evaluate_gnn_readiness_10():
    task_name = "10_gnn_readiness"
    print(f"Đang thực hiện {task_name}...")

    # 1. Thống kê theo Brand (Cạnh tiềm năng: Product - Brand - Product)
    brand_counts = df_clean['brand_label'].value_counts()
    # 2. Thống kê theo Article Type (Cạnh tiềm năng: Product - Type - Product)
    type_counts = df_clean['articleType_label'].value_counts()
    
    # 3. Vẽ biểu đồ phân phối (Log Scale)
    plt.figure(figsize=(10, 6))
    sns.histplot(brand_counts, bins=50, log_scale=(True, False), color='salmon', kde=True)
    plt.title('Phân phối kết nối: Số lượng sản phẩm trên mỗi Brand', fontsize=14)
    plt.xlabel('Số lượng sản phẩm trong một Brand (Log Scale)')
    plt.ylabel('Số lượng Brand (Tần suất)')
    plt.grid(axis='y', alpha=0.3)
    
    plt.savefig(os.path.join(output_eda, f"{task_name}_connectivity.png"), dpi=300, bbox_inches='tight')
    plt.close()

    # 4. Tính toán các chỉ số chuyên sâu cho GNN
    total_products = len(df_clean)
    num_brands = len(brand_counts)
    num_types = len(type_counts)
    
    brand_isolates = (brand_counts == 1).sum()
    type_isolates = (type_counts == 1).sum()

    # 5. Ghi báo cáo .txt (UTF-8)
    report_path = os.path.join(output_eda, f"{task_name}_report.txt")
    with open(report_path, "w", encoding='utf-8') as f:
        f.write(f"Tổng số Nodes (Sản phẩm): {total_products:,}\n\n")
        
        f.write("[PHÂN TÍCH THEO BRAND (Potential Clusters)]\n")
        f.write(f"- Tổng số Brand unique:         {num_brands:,}\n")
        f.write(f"- Trung bình sản phẩm/Brand:    {brand_counts.mean():.2f}\n")
        f.write(f"- Brand lớn nhất (Max Hub):     {brand_counts.max()} sản phẩm\n")
        f.write(f"- Số Brand cô lập (1 sản phẩm): {brand_isolates} ({brand_isolates/num_brands*100:.2f}%)\n\n")
        
        f.write("[PHÂN TÍCH THEO ARTICLE TYPE (Homophily)]\n")
        f.write(f"- Tổng số Type unique:          {num_types:,}\n")
        f.write(f"- Trung bình sản phẩm/Type:     {type_counts.mean():.2f}\n")
        f.write(f"- Type phổ biến nhất:           {type_counts.max()} sản phẩm\n")
        f.write(f"- Số Type cô lập:               {type_isolates} ({type_isolates/num_types*100:.2f}%)\n")
        
        f.write("\n" + "-"*60 + "\n")
        f.write("ĐÁNH GIÁ TÍNH SẴN SÀNG CHO GNN:\n")
        
        # Nhận xét chuyên môn
        if brand_isolates / num_brands > 0.5:
            f.write("- Cảnh báo: Đồ thị dựa trên Brand bị rời rạc cao (High Sparsity).\n")
        else:
            f.write("- Tốt: Đồ thị có độ kết nối ổn định qua Brand.\n")
            
        f.write(f"- Dự kiến số cạnh (Edges) nếu nối qua Brand: {sum([n*(n-1)/2 for n in brand_counts]):,.0f}\n")
        f.write("- Lời khuyên: Với GPU 4GB, nên sử dụng Sparse Tensors để tránh tràn bộ nhớ khi xây dựng Adjacency Matrix.\n")

if __name__ == "__main__":
    verify_zero_null_1()
    check_price_distribution_2()
    analyze_deduplication_impact_3()
    check_label_diversity_4()
    check_onehot_sparsity_5()
    analyze_text_shrinkage_6()
    analyze_correlation_7()
    generate_clean_wordcloud_8()
    check_post_scaling_outliers_9()
    evaluate_gnn_readiness_10()