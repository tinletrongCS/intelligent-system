import { useEffect, useState } from 'react';
import { DollarSign, Package, ShoppingBag, Users, Heart, MessageSquare } from 'lucide-react';
import { apiService, DashboardMetrics } from '@/services/api';

export function Dashboard() {
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
  const [error, setError] = useState('');

  useEffect(() => {
    apiService.getDashboardMetrics()
      .then(setMetrics)
      .catch((err) => setError(err instanceof Error ? err.message : 'Không tải được dashboard'));
  }, []);

  const summary = metrics?.summary;
  const stats = [
    { title: 'Doanh thu', value: `${Number(summary?.revenue || 0).toLocaleString('vi-VN')}₫`, icon: DollarSign, color: 'bg-green-500' },
    { title: 'Đơn hàng', value: String(summary?.orders || 0), icon: ShoppingBag, color: 'bg-blue-500' },
    { title: 'Người dùng', value: String(summary?.users || 0), icon: Users, color: 'bg-purple-500' },
    { title: 'Sản phẩm', value: String(summary?.products || 0), icon: Package, color: 'bg-orange-500' },
    { title: 'Wishlist', value: String(summary?.wishlist_items || 0), icon: Heart, color: 'bg-red-500' },
    { title: 'Feedback', value: String(summary?.feedbacks || 0), icon: MessageSquare, color: 'bg-indigo-500' },
  ];

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="mb-8 text-3xl font-bold">Dashboard Quản Trị</h1>
      {error && <div className="mb-4 rounded-lg bg-red-50 p-3 text-red-600">{error}</div>}
      {!metrics ? (
        <div className="rounded-lg bg-white p-8 text-gray-600 shadow-sm">Đang tải dữ liệu dashboard...</div>
      ) : (
        <>
          <div className="mb-8 grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
            {stats.map((stat) => (
              <div key={stat.title} className="rounded-lg bg-white p-6 shadow-sm">
                <div className="mb-4 flex items-center justify-between">
                  <div className={`${stat.color} flex h-12 w-12 items-center justify-center rounded-lg`}>
                    <stat.icon className="h-6 w-6 text-white" />
                  </div>
                </div>
                <p className="mb-1 text-sm text-gray-600">{stat.title}</p>
                <p className="text-2xl font-bold">{stat.value}</p>
              </div>
            ))}
          </div>

          <div className="rounded-lg bg-white p-6 shadow-sm">
            <h2 className="mb-4 text-xl font-bold">Top sản phẩm</h2>
            <div className="space-y-4">
              {metrics.top_products.map((product, index) => (
                <div key={product.id} className="flex items-center justify-between gap-4 border-b pb-3 last:border-0">
                  <div className="flex min-w-0 items-center gap-3">
                    <div className="flex h-8 w-8 items-center justify-center rounded-full bg-blue-100 font-bold text-blue-600">{index + 1}</div>
                    <div className="min-w-0">
                      <p className="truncate font-medium">{product.name}</p>
                      <p className="text-sm text-gray-600">Đã bán: {product.sold}</p>
                    </div>
                  </div>
                  <p className="font-bold text-green-600">{product.revenue.toLocaleString('vi-VN')}₫</p>
                </div>
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  );
}
