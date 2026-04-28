import { Sparkles } from 'lucide-react';
import { ProductCard, Product } from './ProductCard';

interface RecommendedProductsProps {
  products: Product[];
  onAddToCart: (product: Product) => void;
  onAddToWishlist?: (product: Product) => void;
}

export function RecommendedProducts({ products, onAddToCart, onAddToWishlist }: RecommendedProductsProps) {
  return (
    <div className="bg-gradient-to-r from-purple-50 to-blue-50">
      <div className="container mx-auto px-4 py-8">
        <div className="flex items-center gap-3 mb-6">
          <Sparkles className="w-8 h-8 text-purple-600 fill-current" />
          <div>
            <h2 className="text-2xl font-bold">Gợi ý dành cho bạn</h2>
            <p className="text-gray-600">Dựa trên sở thích và lịch sử mua hàng của bạn</p>
          </div>
        </div>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
          {products.map((product) => (
            <ProductCard key={product.id} product={product} onAddToCart={onAddToCart} onAddToWishlist={onAddToWishlist} />
          ))}
        </div>
      </div>
    </div>
  );
}
