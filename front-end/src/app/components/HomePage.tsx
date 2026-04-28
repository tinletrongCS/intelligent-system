import { ChevronRight, Zap, Truck, Shield, Clock } from 'lucide-react';
import { ProductCard, Product } from './ProductCard';
import { ImageWithFallback } from './figma/ImageWithFallback';
import { RecommendedProducts } from './RecommendedProducts';

interface HomePageProps {
  products: Product[];
  recommendedProducts?: Product[];
  onAddToCart: (product: Product) => void;
  onAddToWishlist?: (product: Product) => void;
}

const categories = [
  { name: 'Apparel', image: 'https://images.unsplash.com/photo-1489987707025-afc232f7ea0f?w=400' },
  { name: 'Footwear', image: 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400' },
  { name: 'Bottomwear', image: 'https://images.unsplash.com/photo-1541099649105-f69ad21f3246?w=400' },
  { name: 'Sports', image: 'https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?w=400' },
  { name: 'Casual', image: 'https://images.unsplash.com/photo-1496747611176-843222e1e57c?w=400' },
  { name: 'Accessories', image: 'https://images.unsplash.com/photo-1515562141207-7a88fb7ce338?w=400' },
];

const features = [
  { icon: Truck, title: 'Miễn phí vận chuyển', description: 'Cho đơn hàng từ 500k' },
  { icon: Shield, title: 'Sản phẩm chọn lọc', description: 'Dữ liệu từ hệ thống gợi ý' },
  { icon: Clock, title: 'Cập nhật nhanh', description: 'Đồng bộ trực tiếp từ API' },
  { icon: Zap, title: 'Gợi ý cá nhân', description: 'Dựa trên hành vi người dùng' },
];

export function HomePage({ products, recommendedProducts = [], onAddToCart, onAddToWishlist }: HomePageProps) {
  const flashSaleProducts = products.filter(p => p.discount && p.discount > 0).slice(0, 10);
  const newProducts = products.slice(0, 8);
  const displayedRecommendations = recommendedProducts.length ? recommendedProducts : products.slice(3, 8);

  return (
    <div className="space-y-12 pb-12">
      {/* Hero Banner */}
      <div className="relative h-[400px] bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg overflow-hidden">
        <div className="absolute inset-0 flex items-center">
          <div className="container mx-auto px-4">
            <div className="max-w-xl text-white">
              <h1 className="text-5xl font-bold mb-4">Thời trang gợi ý cho bạn</h1>
              <p className="text-xl mb-6">Khám phá sản phẩm thời trang được đồng bộ trực tiếp từ backend</p>
              <button className="bg-white text-blue-600 px-8 py-3 rounded-lg font-medium hover:bg-gray-100 transition-colors">
                Khám phá ngay
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Features */}
      <div className="container mx-auto px-4">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
          {features.map((feature, index) => (
            <div key={index} className="flex items-center gap-3 p-4 bg-gray-50 rounded-lg">
              <feature.icon className="w-10 h-10 text-blue-600 flex-shrink-0" />
              <div>
                <h3 className="font-medium">{feature.title}</h3>
                <p className="text-sm text-gray-600">{feature.description}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Categories */}
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold">Danh mục nổi bật</h2>
          <button className="flex items-center gap-1 text-blue-600 hover:gap-2 transition-all">
            Xem tất cả <ChevronRight className="w-5 h-5" />
          </button>
        </div>
        <div className="grid grid-cols-3 md:grid-cols-6 gap-4">
          {categories.map((category, index) => (
            <div key={index} className="group cursor-pointer">
              <div className="aspect-square rounded-lg overflow-hidden mb-2 bg-gray-100">
                <ImageWithFallback
                  src={category.image}
                  alt={category.name}
                  className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-300"
                />
              </div>
              <p className="text-center font-medium">{category.name}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Flash Sale */}
      <div className="bg-red-50">
        <div className="container mx-auto px-4 py-8">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-3">
              <Zap className="w-8 h-8 text-red-600 fill-current" />
              <h2 className="text-2xl font-bold">Sản phẩm giảm giá</h2>
              <div className="flex gap-2 ml-4">
                <div className="bg-red-600 text-white px-3 py-1 rounded">12</div>
                <div className="bg-red-600 text-white px-3 py-1 rounded">34</div>
                <div className="bg-red-600 text-white px-3 py-1 rounded">56</div>
              </div>
            </div>
            <button className="flex items-center gap-1 text-red-600 hover:gap-2 transition-all">
              Xem tất cả <ChevronRight className="w-5 h-5" />
            </button>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-4">
            {(flashSaleProducts.length ? flashSaleProducts : products.slice(0, 5)).map((product) => (
              <ProductCard key={product.id} product={product} onAddToCart={onAddToCart} onAddToWishlist={onAddToWishlist} />
            ))}
          </div>
        </div>
      </div>

      {/* Recommended Products */}
      <RecommendedProducts products={displayedRecommendations} onAddToCart={onAddToCart} onAddToWishlist={onAddToWishlist} />

      {/* New Products */}
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold">Sản phẩm mới</h2>
          <button className="flex items-center gap-1 text-blue-600 hover:gap-2 transition-all">
            Xem tất cả <ChevronRight className="w-5 h-5" />
          </button>
        </div>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
          {newProducts.length === 0 ? (
            <div className="col-span-full rounded-lg border border-dashed bg-white p-8 text-center text-gray-600">
              Chưa có sản phẩm. Hãy chạy backend và seed dữ liệu products.
            </div>
          ) : (
            newProducts.map((product) => (
              <ProductCard key={product.id} product={product} onAddToCart={onAddToCart} onAddToWishlist={onAddToWishlist} />
            ))
          )}
        </div>
      </div>
    </div>
  );
}
