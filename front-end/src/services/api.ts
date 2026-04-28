// API configuration and base setup
const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000').replace(/\/$/, '');

export interface LoginResponse {
  access_token: string;
  token_type: string;
}

export interface UserData {
  id: string;
  username: string;
  email?: string;
  role_id?: number;
  gender?: string;
  age?: number;
  created_at?: string;
  updated_at?: string;
}

export interface RegisterData {
  username: string;
  email: string;
  password: string;
  gender?: string;
  age?: number;
}

export interface BackendProduct {
  id: string;
  brand_name: string;
  product_display_name: string;
  price: number;
  image_url?: string | null;
  description?: string | null;
  style_note?: string | null;
  occasion?: string | null;
  is_active: boolean;
  discounted_price?: number | null;
  gender?: string | null;
  master_category?: string | null;
  sub_category?: string | null;
  article_type?: string | null;
  base_colour?: string | null;
  season?: string | null;
  usage?: string | null;
  myntra_rating?: number | null;
  quantity_in_stock?: number | null;
  created_at: string;
  updated_at: string;
}

export interface CartItemResponse {
  id: number;
  user_id: string;
  product_id: string;
  quantity: number;
  product?: BackendProduct | null;
}

export interface WishlistItemResponse {
  id: string;
  user_id: string;
  product_id: string;
  product?: BackendProduct | null;
}

export interface FeedbackResponse {
  id: string;
  user_id: string;
  product_id: string;
  rank: number;
  created_at: string;
  updated_at: string;
}

export interface OrderResponse {
  id: string;
  user_id: string;
  order_date: string;
  status: number | string;
  total_amount: number;
  note?: string | null;
  items: Array<{
    id: number;
    product_id: string;
    quantity: number;
    unit_price: number;
    subtotal: number;
    product?: BackendProduct | null;
  }>;
  updated_at: string;
}

export interface RecommendationItem {
  product_id: string;
  score: number;
  rank: number;
  product_details?: BackendProduct | null;
}

export interface DashboardMetrics {
  summary: {
    products: number;
    orders: number;
    users: number;
    revenue: number;
    cart_items: number;
    wishlist_items: number;
    feedbacks: number;
  };
  top_products: Array<{
    id: string;
    name: string;
    image_url?: string | null;
    sold: number;
    revenue: number;
  }>;
}

class APIService {
  private getToken(): string | null {
    return localStorage.getItem('access_token');
  }

  private getHeaders(): HeadersInit {
    const token = this.getToken();
    const headers: HeadersInit = { 'Content-Type': 'application/json' };
    if (token) headers.Authorization = `Bearer ${token}`;
    return headers;
  }

  private async parseResponse<T>(response: Response, fallbackMessage: string): Promise<T> {
    const contentType = response.headers.get('content-type') || '';
    const payload = contentType.includes('application/json') ? await response.json() : await response.text();
    if (!response.ok) {
      const detail = typeof payload === 'object' ? payload.detail || payload.message : payload;
      throw new Error(Array.isArray(detail) ? detail.map((item) => item.msg).join(', ') : detail || fallbackMessage);
    }
    return payload as T;
  }

  decodeToken(token: string): Partial<UserData> {
    try {
      const payload = token.split('.')[1];
      const normalized = payload.replace(/-/g, '+').replace(/_/g, '/').padEnd(Math.ceil(payload.length / 4) * 4, '=');
      const decoded = JSON.parse(atob(normalized));
      return { id: decoded.sub };
    } catch {
      return {};
    }
  }

  async login(username: string, password: string): Promise<LoginResponse> {
    const formData = new URLSearchParams();
    formData.append('username', username);
    formData.append('password', password);
    const response = await fetch(`${API_BASE_URL}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: formData,
    });
    return this.parseResponse<LoginResponse>(response, 'Login failed');
  }

  async register(data: RegisterData): Promise<UserData> {
    const response = await fetch(`${API_BASE_URL}/auth/register`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify(data),
    });
    return this.parseResponse<UserData>(response, 'Registration failed');
  }

  async getCurrentUser(): Promise<UserData> {
    const response = await fetch(`${API_BASE_URL}/users/me`, { headers: this.getHeaders() });
    return this.parseResponse<UserData>(response, 'Failed to fetch current user');
  }

  async listUsers(): Promise<UserData[]> {
    const response = await fetch(`${API_BASE_URL}/users`, { headers: this.getHeaders() });
    return this.parseResponse<UserData[]>(response, 'Failed to fetch users');
  }

  async getProducts(skip = 0, limit = 100): Promise<BackendProduct[]> {
    const response = await fetch(`${API_BASE_URL}/products/?skip=${skip}&limit=${limit}`, { headers: this.getHeaders() });
    return this.parseResponse<BackendProduct[]>(response, 'Failed to fetch products');
  }

  async getProductById(id: string): Promise<BackendProduct> {
    const response = await fetch(`${API_BASE_URL}/products/${id}`, { headers: this.getHeaders() });
    return this.parseResponse<BackendProduct>(response, 'Failed to fetch product');
  }

  async addToCart(productId: string, quantity: number): Promise<CartItemResponse> {
    const response = await fetch(`${API_BASE_URL}/cart`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify({ product_id: productId, quantity }),
    });
    return this.parseResponse<CartItemResponse>(response, 'Failed to add to cart');
  }

  async getCart(): Promise<CartItemResponse[]> {
    const response = await fetch(`${API_BASE_URL}/cart`, { headers: this.getHeaders() });
    return this.parseResponse<CartItemResponse[]>(response, 'Failed to fetch cart');
  }

  async updateCartItem(productId: string, quantity: number): Promise<CartItemResponse> {
    const response = await fetch(`${API_BASE_URL}/cart/${productId}`, {
      method: 'PATCH',
      headers: this.getHeaders(),
      body: JSON.stringify({ product_id: productId, quantity }),
    });
    return this.parseResponse<CartItemResponse>(response, 'Failed to update cart');
  }

  async removeCartItem(productId: string): Promise<{ message: string }> {
    const response = await fetch(`${API_BASE_URL}/cart/${productId}`, { method: 'DELETE', headers: this.getHeaders() });
    return this.parseResponse<{ message: string }>(response, 'Failed to remove cart item');
  }

  async addToWishlist(productId: string): Promise<WishlistItemResponse> {
    const response = await fetch(`${API_BASE_URL}/wishlist`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify({ product_id: productId }),
    });
    return this.parseResponse<WishlistItemResponse>(response, 'Failed to add to wishlist');
  }

  async getWishlist(): Promise<WishlistItemResponse[]> {
    const response = await fetch(`${API_BASE_URL}/wishlist`, { headers: this.getHeaders() });
    return this.parseResponse<WishlistItemResponse[]>(response, 'Failed to fetch wishlist');
  }

  async removeWishlistItem(productId: string): Promise<{ message: string }> {
    const response = await fetch(`${API_BASE_URL}/wishlist/${productId}`, { method: 'DELETE', headers: this.getHeaders() });
    return this.parseResponse<{ message: string }>(response, 'Failed to remove wishlist item');
  }

  async createOrder(items: Array<{ product_id: string; quantity: number }>, note?: string): Promise<OrderResponse> {
    const response = await fetch(`${API_BASE_URL}/orders`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify({ items, note }),
    });
    return this.parseResponse<OrderResponse>(response, 'Failed to create order');
  }

  async getMyOrders(): Promise<OrderResponse[]> {
    const response = await fetch(`${API_BASE_URL}/orders/me`, { headers: this.getHeaders() });
    return this.parseResponse<OrderResponse[]>(response, 'Failed to fetch orders');
  }

  async getAllOrders(): Promise<OrderResponse[]> {
    const response = await fetch(`${API_BASE_URL}/orders`, { headers: this.getHeaders() });
    return this.parseResponse<OrderResponse[]>(response, 'Failed to fetch all orders');
  }

  async createFeedback(userId: string, productId: string, rank: number): Promise<FeedbackResponse> {
    const response = await fetch(`${API_BASE_URL}/feedback/${userId}`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify({ product_id: productId, rank }),
    });
    return this.parseResponse<FeedbackResponse>(response, 'Failed to submit feedback');
  }

  async getFeedbacksByProduct(productId: string): Promise<FeedbackResponse[]> {
    const response = await fetch(`${API_BASE_URL}/feedback/product/${productId}`, { headers: this.getHeaders() });
    return this.parseResponse<FeedbackResponse[]>(response, 'Failed to fetch feedbacks');
  }

  async getRecommendations(userId: string, k = 10): Promise<RecommendationItem[]> {
    const response = await fetch(`${API_BASE_URL}/predict/${userId}?k=${k}`, { headers: this.getHeaders() });
    return this.parseResponse<RecommendationItem[]>(response, 'Failed to fetch recommendations');
  }


  async updateUserRole(username: string, role_id: number): Promise<{ username: string; new_role: number }> {
    const response = await fetch(`${API_BASE_URL}/auth/${username}/role`, {
      method: 'PATCH',
      headers: this.getHeaders(),
      body: JSON.stringify({ role_id }),
    });
    return this.parseResponse<{ username: string; new_role: number }>(response, 'Failed to update user role');
  }

  async deleteUser(userId: string): Promise<{ message: string }> {
    const response = await fetch(`${API_BASE_URL}/users/${userId}`, {
      method: 'DELETE',
      headers: this.getHeaders(),
    });
    return this.parseResponse<{ message: string }>(response, 'Failed to delete user');
  }

  async createProduct(data: Partial<BackendProduct>): Promise<BackendProduct> {
    const response = await fetch(`${API_BASE_URL}/products/`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify(data),
    });
    return this.parseResponse<BackendProduct>(response, 'Failed to create product');
  }

  async updateProduct(productId: string, data: Partial<BackendProduct>): Promise<BackendProduct> {
    const response = await fetch(`${API_BASE_URL}/products/${productId}`, {
      method: 'PUT',
      headers: this.getHeaders(),
      body: JSON.stringify(data),
    });
    return this.parseResponse<BackendProduct>(response, 'Failed to update product');
  }

  async deleteProduct(productId: string): Promise<{ message: string }> {
    const response = await fetch(`${API_BASE_URL}/products/${productId}`, {
      method: 'DELETE',
      headers: this.getHeaders(),
    });
    return this.parseResponse<{ message: string }>(response, 'Failed to delete product');
  }

  async updateOrderStatus(orderId: string, statusValue: number): Promise<OrderResponse> {
    const response = await fetch(`${API_BASE_URL}/orders/${orderId}/status?status_value=${statusValue}`, {
      method: 'PATCH',
      headers: this.getHeaders(),
    });
    return this.parseResponse<OrderResponse>(response, 'Failed to update order status');
  }

  async getDashboardMetrics(): Promise<DashboardMetrics> {
    const response = await fetch(`${API_BASE_URL}/dashboard/metrics`, { headers: this.getHeaders() });
    return this.parseResponse<DashboardMetrics>(response, 'Failed to fetch dashboard metrics');
  }
}

export const apiService = new APIService();
