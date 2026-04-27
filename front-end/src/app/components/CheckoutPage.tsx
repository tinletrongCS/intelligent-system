import { useState } from 'react';
import { MapPin, Phone, Mail, CreditCard, Truck } from 'lucide-react';
import { CartItem } from './CartSidebar';
import { apiService } from '@/services/api';
import { ImageWithFallback } from './figma/ImageWithFallback';

interface CheckoutPageProps {
  items: CartItem[];
  onComplete: () => void;
}

export function CheckoutPage({ items, onComplete }: CheckoutPageProps) {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [formData, setFormData] = useState({
    name: '',
    phone: '',
    email: '',
    address: '',
    city: '',
    district: '',
    paymentMethod: 'cod',
    note: '',
  });

  const total = items.reduce((sum, item) => sum + item.price * item.quantity, 0);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (items.length === 0) {
      setError('Giỏ hàng đang trống.');
      return;
    }

    setIsSubmitting(true);
    setError('');
    try {
      await apiService.createOrder(
        items.map((item) => ({ product_id: item.id, quantity: item.quantity })),
        `${formData.name} | ${formData.phone} | ${formData.email} | ${formData.address}, ${formData.district}, ${formData.city} | ${formData.paymentMethod} | ${formData.note}`
      );
      alert('Đặt hàng thành công! Cảm ơn bạn đã mua hàng.');
      onComplete();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Không đặt được đơn hàng');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-8">Thanh toán</h1>

      {error && <div className="mb-4 rounded-lg bg-red-50 p-3 text-red-600">{error}</div>}
      <form onSubmit={handleSubmit} className="grid lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2 space-y-6">
          {/* Shipping Information */}
          <div className="bg-white rounded-lg shadow-sm p-6">
            <div className="flex items-center gap-2 mb-4">
              <MapPin className="w-6 h-6 text-blue-600" />
              <h2 className="text-xl font-bold">Thông tin giao hàng</h2>
            </div>
            <div className="grid md:grid-cols-2 gap-4">
              <input
                type="text"
                name="name"
                placeholder="Họ và tên *"
                required
                value={formData.name}
                onChange={handleChange}
                className="col-span-2 px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <input
                type="tel"
                name="phone"
                placeholder="Số điện thoại *"
                required
                value={formData.phone}
                onChange={handleChange}
                className="px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <input
                type="email"
                name="email"
                placeholder="Email"
                value={formData.email}
                onChange={handleChange}
                className="px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <input
                type="text"
                name="address"
                placeholder="Địa chỉ *"
                required
                value={formData.address}
                onChange={handleChange}
                className="col-span-2 px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <select
                name="city"
                required
                value={formData.city}
                onChange={handleChange}
                className="px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">Tỉnh/Thành phố *</option>
                <option value="hanoi">Hà Nội</option>
                <option value="hcm">TP. Hồ Chí Minh</option>
                <option value="danang">Đà Nẵng</option>
                <option value="haiphong">Hải Phòng</option>
              </select>
              <select
                name="district"
                required
                value={formData.district}
                onChange={handleChange}
                className="px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">Quận/Huyện *</option>
                <option value="district1">Quận 1</option>
                <option value="district2">Quận 2</option>
                <option value="district3">Quận 3</option>
              </select>
              <textarea
                name="note"
                placeholder="Ghi chú đơn hàng"
                value={formData.note}
                onChange={handleChange}
                rows={3}
                className="col-span-2 px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>

          {/* Payment Method */}
          <div className="bg-white rounded-lg shadow-sm p-6">
            <div className="flex items-center gap-2 mb-4">
              <CreditCard className="w-6 h-6 text-blue-600" />
              <h2 className="text-xl font-bold">Phương thức thanh toán</h2>
            </div>
            <div className="space-y-3">
              <label className="flex items-center gap-3 p-4 border rounded-lg cursor-pointer hover:bg-gray-50">
                <input
                  type="radio"
                  name="paymentMethod"
                  value="cod"
                  checked={formData.paymentMethod === 'cod'}
                  onChange={handleChange}
                  className="w-4 h-4"
                />
                <Truck className="w-6 h-6 text-gray-600" />
                <div>
                  <p className="font-medium">Thanh toán khi nhận hàng (COD)</p>
                  <p className="text-sm text-gray-600">Thanh toán bằng tiền mặt khi nhận hàng</p>
                </div>
              </label>
              <label className="flex items-center gap-3 p-4 border rounded-lg cursor-pointer hover:bg-gray-50">
                <input
                  type="radio"
                  name="paymentMethod"
                  value="bank"
                  checked={formData.paymentMethod === 'bank'}
                  onChange={handleChange}
                  className="w-4 h-4"
                />
                <CreditCard className="w-6 h-6 text-gray-600" />
                <div>
                  <p className="font-medium">Chuyển khoản ngân hàng</p>
                  <p className="text-sm text-gray-600">Chuyển khoản qua Internet Banking</p>
                </div>
              </label>
            </div>
          </div>
        </div>

        {/* Order Summary */}
        <div className="lg:col-span-1">
          <div className="bg-white rounded-lg shadow-sm p-6 sticky top-24">
            <h2 className="text-xl font-bold mb-4">Đơn hàng ({items.length} sản phẩm)</h2>
            <div className="space-y-3 mb-4 max-h-60 overflow-y-auto">
              {items.map((item) => (
                <div key={item.id} className="flex gap-3">
                  <div className="relative">
                    <ImageWithFallback
                      src={item.image}
                      alt={item.name}
                      className="w-16 h-16 object-cover rounded"
                    />
                    <span className="absolute -top-2 -right-2 bg-gray-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center">
                      {item.quantity}
                    </span>
                  </div>
                  <div className="flex-1">
                    <p className="text-sm line-clamp-2">{item.name}</p>
                    <p className="text-sm font-medium text-red-600">
                      {item.price.toLocaleString('vi-VN')}₫
                    </p>
                  </div>
                </div>
              ))}
            </div>
            <div className="border-t pt-4 space-y-2">
              <div className="flex justify-between">
                <span className="text-gray-600">Tạm tính:</span>
                <span>{total.toLocaleString('vi-VN')}₫</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Phí vận chuyển:</span>
                <span className="text-green-600">Miễn phí</span>
              </div>
              <div className="flex justify-between text-xl font-bold border-t pt-2">
                <span>Tổng cộng:</span>
                <span className="text-red-600">{total.toLocaleString('vi-VN')}₫</span>
              </div>
            </div>
            <button
              type="submit"
              className="w-full bg-red-600 hover:bg-red-700 text-white py-3 rounded-lg font-medium mt-4 transition-colors"
             disabled={isSubmitting}>
              {isSubmitting ? 'Đang đặt hàng...' : 'Đặt hàng'}
            </button>
          </div>
        </div>
      </form>
    </div>
  );
}
