import { useEffect, useState } from 'react';
import { PackageCheck } from 'lucide-react';
import { apiService, OrderResponse } from '@/services/api';

const statusLabels: Record<string, string> = {
  '0': 'Đang xử lý',
  '1': 'Đang giao',
  '2': 'Hoàn tất',
  '3': 'Đã hủy',
  PENDING: 'Đang xử lý',
  DELIVERING: 'Đang giao',
  COMPLETED: 'Hoàn tất',
  CANCELLED: 'Đã hủy',
};

export function OrdersPage() {
  const [orders, setOrders] = useState<OrderResponse[]>([]);
  const [error, setError] = useState('');

  useEffect(() => {
    apiService.getMyOrders()
      .then(setOrders)
      .catch((err) => setError(err instanceof Error ? err.message : 'Không tải được đơn hàng'));
  }, []);

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="mb-2 text-3xl font-bold">Lịch sử đơn hàng</h1>
      <p className="mb-8 text-gray-600">Các đơn hàng đã đặt qua checkout</p>
      {error && <div className="mb-4 rounded-lg bg-red-50 p-3 text-red-600">{error}</div>}
      {orders.length === 0 ? (
        <div className="flex min-h-[300px] flex-col items-center justify-center rounded-lg border border-dashed bg-white text-gray-500">
          <PackageCheck className="mb-3 h-10 w-10" />
          Chưa có đơn hàng.
        </div>
      ) : (
        <div className="space-y-4">
          {orders.map((order) => (
            <div key={order.id} className="rounded-lg bg-white p-5 shadow-sm">
              <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
                <div>
                  <p className="font-bold">Đơn #{order.id.slice(0, 8)}</p>
                  <p className="text-sm text-gray-500">{new Date(order.order_date).toLocaleString('vi-VN')}</p>
                </div>
                <div className="text-right">
                  <p className="font-bold text-red-600">{order.total_amount.toLocaleString('vi-VN')}₫</p>
                  <p className="text-sm text-gray-600">{statusLabels[String(order.status)] || String(order.status)}</p>
                </div>
              </div>
              <div className="divide-y">
                {order.items.map((item) => (
                  <div key={item.id} className="flex items-center justify-between py-3 text-sm">
                    <span>{item.product?.product_display_name || item.product_id} x {item.quantity}</span>
                    <span>{item.subtotal.toLocaleString('vi-VN')}₫</span>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
