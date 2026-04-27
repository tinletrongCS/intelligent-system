import { PackageSearch } from 'lucide-react';
import { ProductCard, Product } from './ProductCard';

interface ProductsPageProps {
  products: Product[];
  onAddToCart: (product: Product) => void;
  onAddToWishlist?: (product: Product) => void;
}

export function ProductsPage({ products, onAddToCart, onAddToWishlist }: ProductsPageProps) {
  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8 flex items-end justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold">Tất cả sản phẩm</h1>
          <p className="mt-2 text-gray-600">{products.length} sản phẩm thời trang từ backend</p>
        </div>
      </div>

      {products.length === 0 ? (
        <div className="flex min-h-[360px] flex-col items-center justify-center rounded-lg border border-dashed bg-white p-8 text-center">
          <PackageSearch className="mb-4 h-12 w-12 text-gray-400" />
          <h2 className="text-xl font-semibold">Chưa có sản phẩm để hiển thị</h2>
          <p className="mt-2 max-w-md text-gray-600">
            Kiểm tra backend tại http://127.0.0.1:8000 và seed dữ liệu products nếu danh sách vẫn trống.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-2 gap-6 md:grid-cols-3 lg:grid-cols-4">
          {products.map((product) => (
            <ProductCard key={product.id} product={product} onAddToCart={onAddToCart} onAddToWishlist={onAddToWishlist} />
          ))}
        </div>
      )}
    </div>
  );
}
