import torch
import torch.nn as nn
from torchvision import models, transforms
from torch.utils.data import Dataset, DataLoader
from PIL import Image
import pandas as pd
import numpy as np
import os
from tqdm import tqdm

preprocessed_csv = r"E:\Hcmut material\AI\Intelligence System\intelligent-system\data-scientist\standard_dataset\fashion_preprocessed_dataset.csv"
image_path = r"E:\Hcmut material\AI\Intelligence System\archive\fashion-dataset\processed_images"
output_path = r"E:\Hcmut material\AI\Intelligence System\intelligent-system\data-scientist\features\image_features"
os.makedirs(output_path, exist_ok=True)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Đang sử dụng thiết bị: {device}")

# Bước 1: Định nghĩa custom dataset
class FashionImageDataset(Dataset):
    def __init__(self, csv_file, img_dir, transform=None):
        raw_data = pd.read_csv(csv_file)
        raw_data['id'] = raw_data['id'].astype(str)
        
        # Lấy danh sách file thực tế trong thư mục (loại bỏ đuôi .jpg)
        existing_files = set([f.split('.')[0] for f in os.listdir(img_dir) if f.endswith('.jpg')])
        
        # Lọc dataframe: Chỉ giữ lại những dòng mà file ảnh thực sự tồn tại
        self.data = raw_data[raw_data['id'].isin(existing_files)].copy()
        
        diff = len(raw_data) - len(self.data)
        if diff > 0:
            print(f"--- Lưu ý: Đã loại bỏ {diff} ID từ CSV do không tìm thấy file ảnh tương ứng trong thư mục. ---")
            
        self.img_dir = img_dir
        self.transform = transform

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        img_id = self.data.iloc[idx]['id']
        img_path = os.path.join(self.img_dir, f"{img_id}.jpg")
        
        try:
            image = Image.open(img_path).convert('RGB')
        except Exception as e:
            image = Image.new('RGB', (224, 224), (0, 0, 0))
            print(f"Lỗi đọc file {img_id}.jpg: {e}")

        if self.transform:
            image = self.transform(image)
            
        return image, img_id

# Bước 2: Transformations
transform = transforms.Compose([
    transforms.Resize((224, 224)), 
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                         std=[0.229, 0.224, 0.225])
])

# Bước 3: Model Resnet-18 (Giữ nguyên)
def get_resnet18_extractor():
    print("Đang nạp ResNet-18...")
    model = models.resnet18(weights=models.ResNet18_Weights.IMAGENET1K_V1)
    model.fc = nn.Identity()
    model = model.to(device)
    model.eval()
    return model

# Bước 4: Pipeline trích xuất
def extract_visual_features():
    BATCH_SIZE = 64             # GPU 4GB ổn định nhất ở batch_size 32 hoặc 64 cho ResNet18
    dataset = FashionImageDataset(preprocessed_csv, image_path, transform=transform)
    
    if len(dataset) == 0:
        print("Lỗi: Không tìm thấy ảnh hợp lệ nào trong thư mục. Kiểm tra lại đường dẫn!")
        return

    dataloader = DataLoader(dataset, batch_size=BATCH_SIZE, shuffle=False, num_workers=2, pin_memory=True)
    model = get_resnet18_extractor()
    
    all_features = []
    all_ids = []
    
    print(f"Bắt đầu trích xuất cho {len(dataset)} ảnh thực tế...")
    
    with torch.no_grad():
        for inputs, ids in tqdm(dataloader, desc="Đang trích xuất"):
            inputs = inputs.to(device)
            features = model(inputs)
            
            all_features.append(features.cpu().numpy())
            all_ids.extend(ids)
            
    print("\nĐang tổng hợp ma trận đặc trưng...")
    image_features_matrix = np.vstack(all_features)
    
    feature_output_path = os.path.join(output_path, "image_features_resnet18.npy")
    id_output_path = os.path.join(output_path, "image_feature_ids.csv")
    
    np.save(feature_output_path, image_features_matrix)
    pd.DataFrame(all_ids, columns=['id']).to_csv(id_output_path, index=False)
    
    print("="*50)
    print(f"Hoàn thành")
    print(f"Ma trận feature: {image_features_matrix.shape}")
    print(f"File lưu tại: {output_path}")
    print("="*50)

if __name__ == "__main__":
    extract_visual_features()