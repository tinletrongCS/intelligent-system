import { useEffect, useState } from 'react';
import { Package, ShoppingBag, Trash2, Users } from 'lucide-react';
import { apiService, BackendProduct, OrderResponse, UserData } from '@/services/api';
import { useAuth } from '@/context/AuthContext';

const roles: Record<number, string> = { 1: 'Seller', 2: 'Buyer', 3: 'Admin', 4: 'Data Scientist' };
const orderStatuses: Record<number, string> = { 0: 'Pending', 1: 'Delivering', 2: 'Completed', 3: 'Cancelled' };

export function AdminPage() {
  const { user } = useAuth();
  const [tab, setTab] = useState<'users' | 'products' | 'orders'>('users');
  const [users, setUsers] = useState<UserData[]>([]);
  const [products, setProducts] = useState<BackendProduct[]>([]);
  const [orders, setOrders] = useState<OrderResponse[]>([]);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [productForm, setProductForm] = useState({
    id: '',
    brand_name: '',
    product_display_name: '',
    price: '',
    discounted_price: '',
    image_url: '',
    article_type: '',
    master_category: '',
    sub_category: '',
    base_colour: '',
    quantity_in_stock: '100',
  });

  const isAdmin = Number(user?.role_id) === 3;

  const loadAll = () => {
    setError('');
    Promise.allSettled([
      apiService.listUsers(),
      apiService.getProducts(0, 100),
      apiService.getAllOrders(),
    ]).then(([userResult, productResult, orderResult]) => {
      if (userResult.status === 'fulfilled') setUsers(userResult.value);
      if (productResult.status === 'fulfilled') setProducts(productResult.value);
      if (orderResult.status === 'fulfilled') setOrders(orderResult.value);
      const failed = [userResult, productResult, orderResult].find((result) => result.status === 'rejected');
      if (failed && failed.status === 'rejected') setError(failed.reason instanceof Error ? failed.reason.message : 'Không tải được dữ liệu admin');
    });
  };

  useEffect(loadAll, []);

  if (!isAdmin) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="rounded-lg bg-red-50 p-6 text-red-700">Bạn cần đăng nhập bằng tài khoản admin để dùng trang này.</div>
      </div>
    );
  }

  const showMessage = (text: string) => {
    setMessage(text);
    setError('');
    window.setTimeout(() => setMessage(''), 2500);
  };

  const updateUserRole = async (targetUser: UserData, roleId: number) => {
    await apiService.updateUserRole(targetUser.username, roleId);
    setUsers((prev) => prev.map((item) => item.id === targetUser.id ? { ...item, role_id: roleId } : item));
    showMessage('Đã cập nhật role');
  };

  const deleteUser = async (targetUser: UserData) => {
    if (!confirm(`Xóa user ${targetUser.username}?`)) return;
    await apiService.deleteUser(targetUser.id);
    setUsers((prev) => prev.filter((item) => item.id !== targetUser.id));
    showMessage('Đã xóa user');
  };

  const editProduct = (product: BackendProduct) => {
    setTab('products');
    setProductForm({
      id: product.id,
      brand_name: product.brand_name || '',
      product_display_name: product.product_display_name || '',
      price: String(product.price || ''),
      discounted_price: product.discounted_price ? String(product.discounted_price) : '',
      image_url: product.image_url || '',
      article_type: product.article_type || '',
      master_category: product.master_category || '',
      sub_category: product.sub_category || '',
      base_colour: product.base_colour || '',
      quantity_in_stock: String(product.quantity_in_stock ?? 100),
    });
  };

  const resetProductForm = () => setProductForm({ id: '', brand_name: '', product_display_name: '', price: '', discounted_price: '', image_url: '', article_type: '', master_category: '', sub_category: '', base_colour: '', quantity_in_stock: '100' });

  const saveProduct = async (event: React.FormEvent) => {
    event.preventDefault();
    const payload = {
      brand_name: productForm.brand_name,
      product_display_name: productForm.product_display_name,
      price: Number(productForm.price),
      discounted_price: productForm.discounted_price ? Number(productForm.discounted_price) : null,
      image_url: productForm.image_url || null,
      article_type: productForm.article_type || null,
      master_category: productForm.master_category || null,
      sub_category: productForm.sub_category || null,
      base_colour: productForm.base_colour || null,
      quantity_in_stock: Number(productForm.quantity_in_stock || 0),
      is_active: true,
    };
    const saved = productForm.id ? await apiService.updateProduct(productForm.id, payload) : await apiService.createProduct(payload);
    setProducts((prev) => productForm.id ? prev.map((item) => item.id === saved.id ? saved : item) : [saved, ...prev]);
    resetProductForm();
    showMessage(productForm.id ? 'Đã cập nhật sản phẩm' : 'Đã tạo sản phẩm');
  };

  const deleteProduct = async (product: BackendProduct) => {
    if (!confirm(`Xóa sản phẩm ${product.product_display_name}?`)) return;
    await apiService.deleteProduct(product.id);
    setProducts((prev) => prev.filter((item) => item.id !== product.id));
    showMessage('Đã xóa sản phẩm');
  };

  const updateOrderStatus = async (order: OrderResponse, status: number) => {
    const saved = await apiService.updateOrderStatus(order.id, status);
    setOrders((prev) => prev.map((item) => item.id === saved.id ? saved : item));
    showMessage('Đã cập nhật trạng thái đơn hàng');
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-6 flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold">Admin CRUD</h1>
          <p className="text-gray-600">Quản lý user, sản phẩm và đơn hàng</p>
        </div>
        <button onClick={loadAll} className="rounded-lg border px-4 py-2 hover:bg-gray-50">Tải lại</button>
      </div>

      {message && <div className="mb-4 rounded-lg bg-green-50 p-3 text-green-700">{message}</div>}
      {error && <div className="mb-4 rounded-lg bg-red-50 p-3 text-red-700">{error}</div>}

      <div className="mb-6 flex gap-2 rounded-lg bg-gray-100 p-1">
        <button onClick={() => setTab('users')} className={`flex items-center gap-2 rounded-md px-4 py-2 ${tab === 'users' ? 'bg-white shadow-sm text-blue-600' : 'text-gray-600'}`}><Users className="h-4 w-4" />Users</button>
        <button onClick={() => setTab('products')} className={`flex items-center gap-2 rounded-md px-4 py-2 ${tab === 'products' ? 'bg-white shadow-sm text-blue-600' : 'text-gray-600'}`}><Package className="h-4 w-4" />Products</button>
        <button onClick={() => setTab('orders')} className={`flex items-center gap-2 rounded-md px-4 py-2 ${tab === 'orders' ? 'bg-white shadow-sm text-blue-600' : 'text-gray-600'}`}><ShoppingBag className="h-4 w-4" />Orders</button>
      </div>

      {tab === 'users' && (
        <div className="overflow-x-auto rounded-lg bg-white shadow-sm">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 text-left"><tr><th className="p-3">Username</th><th className="p-3">Email</th><th className="p-3">Role</th><th className="p-3">Action</th></tr></thead>
            <tbody className="divide-y">
              {users.map((item) => (
                <tr key={item.id}>
                  <td className="p-3 font-medium">{item.username}</td>
                  <td className="p-3">{item.email}</td>
                  <td className="p-3"><select value={Number(item.role_id || 2)} onChange={(e) => updateUserRole(item, Number(e.target.value))} className="rounded border px-2 py-1">{Object.entries(roles).map(([id, label]) => <option key={id} value={id}>{label}</option>)}</select></td>
                  <td className="p-3"><button onClick={() => deleteUser(item)} className="rounded p-2 text-red-600 hover:bg-red-50"><Trash2 className="h-4 w-4" /></button></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {tab === 'products' && (
        <div className="grid gap-6 lg:grid-cols-[360px_1fr]">
          <form onSubmit={saveProduct} className="space-y-3 rounded-lg bg-white p-5 shadow-sm">
            <h2 className="text-xl font-bold">{productForm.id ? 'Sửa sản phẩm' : 'Thêm sản phẩm'}</h2>
            {(['brand_name', 'product_display_name', 'price', 'discounted_price', 'image_url', 'article_type', 'master_category', 'sub_category', 'base_colour', 'quantity_in_stock'] as const).map((field) => (
              <input key={field} required={['brand_name', 'product_display_name', 'price'].includes(field)} placeholder={field} value={productForm[field]} onChange={(e) => setProductForm((prev) => ({ ...prev, [field]: e.target.value }))} className="w-full rounded border px-3 py-2" />
            ))}
            <div className="flex gap-2"><button className="rounded bg-blue-600 px-4 py-2 text-white hover:bg-blue-700">Lưu</button><button type="button" onClick={resetProductForm} className="rounded border px-4 py-2 hover:bg-gray-50">Reset</button></div>
          </form>
          <div className="overflow-x-auto rounded-lg bg-white shadow-sm">
            <table className="w-full text-sm"><thead className="bg-gray-50 text-left"><tr><th className="p-3">Tên</th><th className="p-3">Brand</th><th className="p-3">Giá</th><th className="p-3">Kho</th><th className="p-3">Action</th></tr></thead><tbody className="divide-y">{products.map((product) => <tr key={product.id}><td className="max-w-[320px] truncate p-3 font-medium">{product.product_display_name}</td><td className="p-3">{product.brand_name}</td><td className="p-3">{product.price.toLocaleString('vi-VN')}₫</td><td className="p-3">{product.quantity_in_stock}</td><td className="p-3"><button onClick={() => editProduct(product)} className="mr-2 rounded border px-3 py-1 hover:bg-gray-50">Sửa</button><button onClick={() => deleteProduct(product)} className="rounded px-3 py-1 text-red-600 hover:bg-red-50">Xóa</button></td></tr>)}</tbody></table>
          </div>
        </div>
      )}

      {tab === 'orders' && (
        <div className="space-y-4">
          {orders.map((order) => (
            <div key={order.id} className="rounded-lg bg-white p-5 shadow-sm">
              <div className="flex flex-wrap items-center justify-between gap-3"><div><p className="font-bold">Đơn #{order.id.slice(0, 8)}</p><p className="text-sm text-gray-500">User: {order.user_id}</p></div><div className="text-right"><p className="font-bold text-red-600">{order.total_amount.toLocaleString('vi-VN')}₫</p><select value={Number(order.status)} onChange={(e) => updateOrderStatus(order, Number(e.target.value))} className="rounded border px-2 py-1">{Object.entries(orderStatuses).map(([id, label]) => <option key={id} value={id}>{label}</option>)}</select></div></div>
              <div className="mt-3 divide-y text-sm">{order.items.map((item) => <div key={item.id} className="flex justify-between py-2"><span>{item.product?.product_display_name || item.product_id} x {item.quantity}</span><span>{item.subtotal.toLocaleString('vi-VN')}₫</span></div>)}</div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
