import { Heart, PackageCheck, ShoppingCart, Search, User, Menu, LogOut } from 'lucide-react';
import { Link, useNavigate } from 'react-router-dom';
import { useState } from 'react';
import { useAuth } from '@/context/AuthContext';

interface HeaderProps {
  cartItemCount: number;
  onCartClick: () => void;
}

export function Header({ cartItemCount, onCartClick }: HeaderProps) {
  const [isUserMenuOpen, setIsUserMenuOpen] = useState(false);
  const { isAuthenticated, logout, user } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    setIsUserMenuOpen(false);
    navigate('/login');
  };

  return (
    <header className="sticky top-0 z-50 w-full border-b bg-white">
      <div className="container mx-auto px-4 py-4 flex items-center justify-between">
        <div className="flex items-center gap-8">
          <Link to="/" className="text-2xl font-bold text-blue-600">
            ShopVN
          </Link>
          <nav className="hidden md:flex gap-6">
            <Link to="/" className="hover:text-blue-600 transition-colors">
              Trang chủ
            </Link>
            <Link to="/products" className="hover:text-blue-600 transition-colors">
              Sản phẩm
            </Link>
            <Link to="/wishlist" className="hover:text-blue-600 transition-colors">
              Wishlist
            </Link>
            <Link to="/orders" className="hover:text-blue-600 transition-colors">
              Đơn hàng
            </Link>
            {Number(user?.role_id) === 3 && (
              <>
                <Link to="/admin" className="hover:text-blue-600 transition-colors">
                  Admin
                </Link>
                <Link to="/dashboard" className="hover:text-blue-600 transition-colors">
                  Dashboard
                </Link>
                <Link to="/data-science" className="hover:text-blue-600 transition-colors">
                  Data Science
                </Link>
              </>
            )}
          </nav>
        </div>

        <div className="flex-1 max-w-xl mx-8 hidden md:block">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 w-5 h-5" />
            <input
              type="text"
              placeholder="Tìm kiếm sản phẩm..."
              className="w-full pl-10 pr-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>

        <div className="flex items-center gap-4">
          {isAuthenticated ? (
            <div className="relative">
              <button
                onClick={() => setIsUserMenuOpen(!isUserMenuOpen)}
                className="p-2 hover:bg-gray-100 rounded-lg transition-colors flex items-center gap-2"
              >
                <User className="w-6 h-6" />
                <span className="hidden sm:inline text-sm font-medium truncate max-w-[100px]">
                  {user?.username || 'User'}
                </span>
              </button>
              {isUserMenuOpen && (
                <div className="absolute right-0 mt-2 w-48 bg-white border rounded-lg shadow-lg">
                  <div className="p-3 border-b">
                    <p className="text-sm font-medium">{user?.username}</p>
                    <p className="text-xs text-gray-500">{user?.email}</p>
                  </div>
                  {Number(user?.role_id) === 3 && (
                    <Link to="/admin" onClick={() => setIsUserMenuOpen(false)} className="flex items-center gap-2 px-4 py-2 hover:bg-gray-50 transition-colors">
                      Admin
                    </Link>
                  )}
                  <Link to="/wishlist" onClick={() => setIsUserMenuOpen(false)} className="flex items-center gap-2 px-4 py-2 hover:bg-gray-50 transition-colors">
                    <Heart className="w-4 h-4" />
                    Wishlist
                  </Link>
                  <Link to="/orders" onClick={() => setIsUserMenuOpen(false)} className="flex items-center gap-2 px-4 py-2 hover:bg-gray-50 transition-colors">
                    <PackageCheck className="w-4 h-4" />
                    Đơn hàng
                  </Link>
                  <button
                    onClick={handleLogout}
                    className="w-full flex items-center gap-2 px-4 py-2 text-red-600 hover:bg-red-50 transition-colors"
                  >
                    <LogOut className="w-4 h-4" />
                    Đăng xuất
                  </button>
                </div>
              )}
            </div>
          ) : (
            <Link
              to="/login"
              className="px-3 py-2 text-sm font-medium text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
            >
              Đăng nhập
            </Link>
          )}

          <button
            onClick={onCartClick}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors relative"
          >
            <ShoppingCart className="w-6 h-6" />
            {cartItemCount > 0 && (
              <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center">
                {cartItemCount}
              </span>
            )}
          </button>
          <button className="md:hidden p-2 hover:bg-gray-100 rounded-lg transition-colors">
            <Menu className="w-6 h-6" />
          </button>
        </div>
      </div>
    </header>
  );
}
