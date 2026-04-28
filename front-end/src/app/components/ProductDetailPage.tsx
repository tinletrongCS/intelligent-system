import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { Heart, ShoppingCart, Star } from 'lucide-react';
import { apiService, BackendProduct, FeedbackResponse } from '@/services/api';
import { useAuth } from '@/context/AuthContext';
import { Product } from './ProductCard';
import { ImageWithFallback } from './figma/ImageWithFallback';

interface ProductDetailPageProps {
  onAddToCart: (product: Product) => void;
  onAddToWishlist: (product: Product) => void;
}

function toProduct(product: BackendProduct): Product {
  const price = Number(product.discounted_price || product.price || 0);
  const originalPrice = product.discounted_price && product.discounted_price < product.price ? Number(product.price) : undefined;
  const discount = originalPrice ? Math.round(((originalPrice - price) / originalPrice) * 100) : undefined;
  return {
    id: product.id,
    name: product.product_display_name,
    price,
    originalPrice,
    image: product.image_url || 'https://images.unsplash.com/photo-1445205170230-053b83016050?w=600',
    rating: Number(product.myntra_rating || 0),
    reviews: 0,
    category: product.article_type || product.sub_category || product.master_category || product.brand_name,
    discount,
  };
}

export function ProductDetailPage({ onAddToCart, onAddToWishlist }: ProductDetailPageProps) {
  const { id } = useParams();
  const { user } = useAuth();
  const [product, setProduct] = useState<BackendProduct | null>(null);
  const [feedbacks, setFeedbacks] = useState<FeedbackResponse[]>([]);
  const [rank, setRank] = useState(5);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  useEffect(() => {
    if (!id) return;
    apiService.getProductById(id).then(setProduct).catch((err) => setError(err instanceof Error ? err.message : 'Không tải được sản phẩm'));
    apiService.getFeedbacksByProduct(id).then(setFeedbacks).catch(() => setFeedbacks([]));
  }, [id]);

  const submitFeedback = async () => {
    if (!user?.id || !product) return setError('Cần đăng nhập để đánh giá sản phẩm');
    try {
      const saved = await apiService.createFeedback(user.id, product.id, rank);
      setFeedbacks((prev) => [saved, ...prev.filter((item) => item.user_id !== user.id)]);
      setMessage('Đã lưu đánh giá');
      setError('');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Không gửi được đánh giá');
    }
  };

  if (error && !product) return <div className="container mx-auto px-4 py-8 text-red-600">{error}</div>;
  if (!product) return <div className="container mx-auto px-4 py-8">Đang tải sản phẩm...</div>;

  const viewProduct = toProduct(product);
  const avgRating = feedbacks.length ? feedbacks.reduce((sum, item) => sum + item.rank, 0) / feedbacks.length : viewProduct.rating;

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="grid gap-8 lg:grid-cols-2">
        <div className="rounded-lg bg-white p-4 shadow-sm">
          <ImageWithFallback src={viewProduct.image} alt={viewProduct.name} className="aspect-square w-full rounded-lg object-cover" />
        </div>
        <div className="space-y-5">
          <div>
            <p className="text-sm text-gray-500">{product.brand_name} / {viewProduct.category}</p>
            <h1 className="mt-2 text-3xl font-bold">{viewProduct.name}</h1>
          </div>
          <div className="flex items-center gap-2">
            {[...Array(5)].map((_, index) => <Star key={index} className={`h-5 w-5 ${index < Math.round(avgRating) ? 'fill-yellow-400 text-yellow-400' : 'text-gray-300'}`} />)}
            <span className="text-gray-600">{avgRating.toFixed(1)} ({feedbacks.length} đánh giá)</span>
          </div>
          <div className="flex items-baseline gap-3">
            <span className="text-3xl font-bold text-red-600">{viewProduct.price.toLocaleString('vi-VN')}₫</span>
            {viewProduct.originalPrice && <span className="text-gray-400 line-through">{viewProduct.originalPrice.toLocaleString('vi-VN')}₫</span>}
          </div>
          <div className="grid grid-cols-2 gap-3 text-sm text-gray-700">
            <div className="rounded-lg bg-white p-3 shadow-sm">Màu: <b>{product.base_colour || '-'}</b></div>
            <div className="rounded-lg bg-white p-3 shadow-sm">Mùa: <b>{product.season || '-'}</b></div>
            <div className="rounded-lg bg-white p-3 shadow-sm">Giới tính: <b>{product.gender || '-'}</b></div>
            <div className="rounded-lg bg-white p-3 shadow-sm">Tồn kho: <b>{product.quantity_in_stock ?? '-'}</b></div>
          </div>
          <p className="text-gray-700 leading-7">{product.description || product.style_note || 'Chưa có mô tả.'}</p>
          <div className="flex gap-3">
            <button onClick={() => onAddToCart(viewProduct)} className="flex items-center gap-2 rounded-lg bg-blue-600 px-5 py-3 text-white hover:bg-blue-700"><ShoppingCart className="h-5 w-5" />Thêm vào giỏ</button>
            <button onClick={() => onAddToWishlist(viewProduct)} className="flex items-center gap-2 rounded-lg border px-5 py-3 text-red-600 hover:bg-red-50"><Heart className="h-5 w-5" />Yêu thích</button>
          </div>
          {message && <p className="text-green-600">{message}</p>}
          {error && <p className="text-red-600">{error}</p>}
        </div>
      </div>

      <div className="mt-8 rounded-lg bg-white p-6 shadow-sm">
        <h2 className="mb-4 text-xl font-bold">Đánh giá sản phẩm</h2>
        <div className="mb-6 flex flex-wrap items-center gap-3">
          <select value={rank} onChange={(e) => setRank(Number(e.target.value))} className="rounded-lg border px-3 py-2">
            {[5, 4, 3, 2, 1].map((value) => <option key={value} value={value}>{value} sao</option>)}
          </select>
          <button onClick={submitFeedback} className="rounded-lg bg-blue-600 px-4 py-2 text-white hover:bg-blue-700">Gửi đánh giá</button>
        </div>
        <div className="space-y-3">
          {feedbacks.length === 0 ? <p className="text-gray-500">Chưa có đánh giá.</p> : feedbacks.map((item) => (
            <div key={item.id} className="rounded-lg border p-3">
              <div className="flex items-center gap-2">{[...Array(5)].map((_, index) => <Star key={index} className={`h-4 w-4 ${index < item.rank ? 'fill-yellow-400 text-yellow-400' : 'text-gray-300'}`} />)}</div>
              <p className="mt-1 text-sm text-gray-500">User: {item.user_id}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
