import { useEffect, useState } from 'react';
import { HeartOff } from 'lucide-react';
import { apiService, WishlistItemResponse } from '@/services/api';
import { ProductCard, Product } from './ProductCard';

interface WishlistPageProps {
  onAddToCart: (product: Product) => void;
}

function toProduct(item: WishlistItemResponse): Product | null {
  const product = item.product;
  if (!product) return null;
  const price = Number(product.discounted_price || product.price || 0);
  const originalPrice = product.discounted_price && product.discounted_price < product.price ? Number(product.price) : undefined;
  return {
    id: product.id,
    name: product.product_display_name,
    price,
    originalPrice,
    image: product.image_url || 'https://images.unsplash.com/photo-1445205170230-053b83016050?w=600',
    rating: Number(product.myntra_rating || 0),
    reviews: 0,
    category: product.article_type || product.sub_category || product.master_category || product.brand_name,
    discount: originalPrice ? Math.round(((originalPrice - price) / originalPrice) * 100) : undefined,
  };
}

export function WishlistPage({ onAddToCart }: WishlistPageProps) {
  const [items, setItems] = useState<Product[]>([]);
  const [error, setError] = useState('');

  const loadWishlist = () => {
    apiService.getWishlist()
      .then((data) => setItems(data.map(toProduct).filter((item): item is Product => Boolean(item))))
      .catch((err) => setError(err instanceof Error ? err.message : 'Không tải được wishlist'));
  };

  useEffect(loadWishlist, []);

  const remove = async (product: Product) => {
    await apiService.removeWishlistItem(product.id);
    setItems((prev) => prev.filter((item) => item.id !== product.id));
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="mb-2 text-3xl font-bold">Wishlist</h1>
      <p className="mb-8 text-gray-600">Các sản phẩm bạn đã đánh dấu yêu thích</p>
      {error && <div className="mb-4 rounded-lg bg-red-50 p-3 text-red-600">{error}</div>}
      {items.length === 0 ? (
        <div className="flex min-h-[300px] flex-col items-center justify-center rounded-lg border border-dashed bg-white text-gray-500">
          <HeartOff className="mb-3 h-10 w-10" />
          Wishlist đang trống.
        </div>
      ) : (
        <div className="grid grid-cols-2 gap-6 md:grid-cols-3 lg:grid-cols-4">
          {items.map((product) => <ProductCard key={product.id} product={product} onAddToCart={onAddToCart} onAddToWishlist={remove} />)}
        </div>
      )}
    </div>
  );
}
