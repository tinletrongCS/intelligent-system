import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
import os
import pandas as pd
from torch_geometric.data import Data
from torch_geometric.nn import GCNConv, GAE
from torch_geometric.utils import train_test_split_edges
from tqdm import tqdm

path_node_features = r"E:\Hcmut material\AI\Intelligence System\intelligent-system\data-scientist\features\final_node_features\final_node_features.npy"
path_edge_index = r"E:\Hcmut material\AI\Intelligence System\intelligent-system\data-scientist\features\graph_data\edge_index.npy"
path_mapping = r"E:\Hcmut material\AI\Intelligence System\intelligent-system\data-scientist\features\graph_data\id_to_idx_mapping.csv"

model_output_path = r"E:\Hcmut material\AI\Intelligence System\intelligent-system\data-scientist\features\models"
embedding_output_path = r"E:\Hcmut material\AI\Intelligence System\intelligent-system\data-scientist\features\models\final_gnn_embeddings"

os.makedirs(model_output_path, exist_ok=True)
os.makedirs(embedding_output_path, exist_ok=True)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Đang sử dụng thiết bị: {device}")

def prepare_graph_data():
    print("--- Đang nạp dữ liệu đồ thị ---")
    
    # Nạp Node Features và Edge Index từ đường dẫn ông cung cấp
    x_np = np.load(path_node_features)
    edge_index_np = np.load(path_edge_index)
    
    # Chuyển sang Tensor
    x = torch.from_numpy(x_np).to(torch.float32)
    edge_index = torch.from_numpy(edge_index_np).to(torch.long)
    
    # Tạo đối tượng Data của PyTorch Geometric
    data = Data(x=x, edge_index=edge_index)
    
    # Chia cạnh: 85% train, 5% val, 10% test (Học Link Prediction)
    print("Đang thực hiện Train/Val/Test Split cho Edges...")
    data = train_test_split_edges(data, val_ratio=0.05, test_ratio=0.1)
    
    return data.to(device)

class GCNEncoder(nn.Module):
    def __init__(self, in_channels, hidden_channels, out_channels):
        super(GCNEncoder, self).__init__()
        # Lớp 1: Học đặc trưng lân cận
        self.conv1 = GCNConv(in_channels, hidden_channels)
        # Lớp 2: Nén thành Embedding cuối cùng
        self.conv2 = GCNConv(hidden_channels, out_channels)

    def forward(self, x, edge_index):
        x = self.conv1(x, edge_index).relu()
        x = F.dropout(x, p=0.2, training=self.training) # Dropout 20% để tránh overfit
        return self.conv2(x, edge_index)

def train_gnn():
    data = prepare_graph_data()
    num_features = data.num_features
    
    # Khởi tạo GAE (Encoder nén về 128 chiều)
    # 916 -> 256 -> 128
    model = GAE(GCNEncoder(num_features, 256, 128)).to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=0.01)

    print(f"\nBắt đầu huấn luyện: Input({num_features}) -> Hidden(256) -> Output(128)")
    
    model.train()
    for epoch in range(1, 101): # Huấn luyện 100 Epoch
        optimizer.zero_grad()
        
        # Bước Encode: Trích xuất Latent Vector (z)
        z = model.encode(data.x, data.train_pos_edge_index)
        
        # Bước Decode & Loss: Tính toán khả năng tái tạo cạnh
        loss = model.recon_loss(z, data.train_pos_edge_index)
        
        loss.backward()
        optimizer.step()

        # In log mỗi 10 epoch
        if epoch % 10 == 0:
            model.eval()
            with torch.no_grad():
                auc, ap = model.test(z, data.val_pos_edge_index, data.val_neg_edge_index)
                print(f"Epoch: {epoch:03d} | Loss: {loss:.4f} | Val AUC: {auc:.4f} | Val AP: {ap:.4f}")
            model.train()

    print("\n--- Huấn luyện hoàn tất! ---")
    
    # Lưu Model State
    model_path = os.path.join(model_output_path, "fashion_gnn_model_v1.pth")
    torch.save(model.state_dict(), model_path)
    
    # Lưu Final Embeddings (Ma trận quan trọng nhất để gợi ý)
    model.eval()
    with torch.no_grad():
        final_embeddings = model.encode(data.x, data.train_pos_edge_index).cpu().numpy()
        emb_path = os.path.join(embedding_output_path, "final_gnn_embeddings.npy")
        np.save(emb_path, final_embeddings)

    print(f"1. Model đã lưu tại: {model_path}")
    print(f"2. Embeddings đã lưu tại: {emb_path}")
    print(f"3. Kích thước Embeddings: {final_embeddings.shape}")
    print("="*50)

if __name__ == "__main__":
    train_gnn()