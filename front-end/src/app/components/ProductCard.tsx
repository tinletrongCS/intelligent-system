import { Heart, ShoppingCart, Star, Eye } from 'lucide-react';
import { Link } from 'react-router-dom';
import { ImageWithFallback } from './figma/ImageWithFallback';

export interface Product {
  id: string;
  name: string;
  price: number;
  originalPrice?: number;
  image: string;
  rating: number;
  reviews: number;
  category: string;
  discount?: number;
}

interface ProductCardProps {
  product: Product;
  onAddToCart: (product: Product) => void;
  onAddToWishlist?: (product: Product) => void;
}

export function ProductCard({ product, onAddToCart, onAddToWishlist }: ProductCardProps) {
  return (
    <div className="bg-white rounded-lg shadow-sm hover:shadow-md transition-shadow overflow-hidden group">
      <Link to={`/products/${product.id}`} className="relative block aspect-square overflow-hidden bg-gray-100">
        <ImageWithFallback src={product.image} alt={product.name} className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300" />
        {product.discount && product.discount > 0 && (
          <span className="absolute top-2 right-2 bg-red-500 text-white px-2 py-1 rounded text-sm font-medium">-{product.discount}%</span>
        )}
      </Link>

      <div className="p-4">
        <p className="text-sm text-gray-500 mb-1">{product.category}</p>
        <Link to={`/products/${product.id}`} className="block font-medium mb-2 line-clamp-2 min-h-[48px] hover:text-blue-600">
          {product.name}
        </Link>

        <div className="flex items-center gap-1 mb-2">
          <div className="flex">
            {[...Array(5)].map((_, i) => (
              <Star key={i} className={`w-4 h-4 ${i < Math.floor(product.rating) ? 'fill-yellow-400 text-yellow-400' : 'text-gray-300'}`} />
            ))}
          </div>
          <span className="text-sm text-gray-500">({product.reviews})</span>
        </div>

        <div className="flex items-center gap-2 mb-3">
          <span className="text-xl font-bold text-red-600">{product.price.toLocaleString('vi-VN')}₫</span>
          {product.originalPrice && <span className="text-sm text-gray-400 line-through">{product.originalPrice.toLocaleString('vi-VN')}₫</span>}
        </div>

        <div className="grid grid-cols-[1fr_auto_auto] gap-2">
          <button onClick={() => onAddToCart(product)} className="bg-blue-600 hover:bg-blue-700 text-white py-2 rounded-lg flex items-center justify-center gap-2 transition-colors">
            <ShoppingCart className="w-4 h-4" />
            Giỏ
          </button>
          <Link to={`/products/${product.id}`} className="border px-3 rounded-lg flex items-center justify-center hover:bg-gray-50" title="Xem chi tiết">
            <Eye className="w-4 h-4" />
          </Link>
          <button onClick={() => onAddToWishlist?.(product)} className="border px-3 rounded-lg flex items-center justify-center hover:bg-red-50 text-red-600" title="Yêu thích">
            <Heart className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
}
