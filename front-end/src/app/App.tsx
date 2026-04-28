import { useEffect, useState } from 'react';
import { BrowserRouter, Routes, Route, useNavigate } from 'react-router-dom';
import { Header } from './components/Header';
import { HomePage } from './components/HomePage';
import { ProductsPage } from './components/ProductsPage';
import { Dashboard } from './components/Dashboard';
import { DataScientistPage } from './components/DataScientistPage';
import { CartSidebar, CartItem } from './components/CartSidebar';
import { CheckoutPage } from './components/CheckoutPage';
import { LoginPage } from './components/LoginPage';
import { RegisterPage } from './components/RegisterPage';
import { ProtectedRoute } from './components/ProtectedRoute';
import { AdminRoute } from './components/AdminRoute';
import { Product } from './components/ProductCard';
import { ProductDetailPage } from './components/ProductDetailPage';
import { WishlistPage } from './components/WishlistPage';
import { OrdersPage } from './components/OrdersPage';
import { AdminPage } from './components/AdminPage';
import { AuthProvider } from '@/context/AuthContext';
import { apiService, BackendProduct } from '@/services/api';
import { useAuth } from '@/context/AuthContext';

const fallbackImage = 'https://images.unsplash.com/photo-1445205170230-053b83016050?w=600';

function toProduct(product: BackendProduct): Product {
  const price = Number(product.discounted_price || product.price || 0);
  const originalPrice = product.discounted_price ? Number(product.price) : undefined;
  const discount = originalPrice && originalPrice > price
    ? Math.round(((originalPrice - price) / originalPrice) * 100)
    : undefined;

  return {
    id: product.id,
    name: product.product_display_name,
    price,
    originalPrice,
    image: product.image_url || fallbackImage,
    rating: Number(product.myntra_rating || 0),
    reviews: 0,
    category: product.article_type || product.sub_category || product.master_category || product.brand_name || 'Sản phẩm',
    discount,
  };
}

function AppContent() {
  const { isAuthenticated, user } = useAuth();
  const [cartItems, setCartItems] = useState<CartItem[]>([]);
  const [isCartOpen, setIsCartOpen] = useState(false);
  const [products, setProducts] = useState<Product[]>([]);
  const [recommendedProducts, setRecommendedProducts] = useState<Product[]>([]);
  const [productsLoading, setProductsLoading] = useState(true);
  const [productsError, setProductsError] = useState<string | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    let isMounted = true;

    apiService.getProducts(0, 100)
      .then((items) => {
        if (isMounted) {
          setProducts(items.map(toProduct));
          setProductsError(null);
        }
      })
      .catch((error) => {
        if (isMounted) {
          setProductsError(error instanceof Error ? error.message : 'Không tải được sản phẩm');
        }
      })
      .finally(() => {
        if (isMounted) {
          setProductsLoading(false);
        }
      });

    return () => {
      isMounted = false;
    };
  }, []);


  useEffect(() => {
    if (!isAuthenticated) {
      setCartItems([]);
      return;
    }

    apiService.getCart()
      .then((items) => {
        setCartItems(items.map((item) => {
          const product = item.product;
          const price = Number(product?.discounted_price || product?.price || 0);
          const originalPrice = product?.discounted_price && product.discounted_price < product.price ? Number(product.price) : undefined;
          return {
            id: item.product_id,
            name: product?.product_display_name || item.product_id,
            price,
            originalPrice,
            image: product?.image_url || fallbackImage,
            rating: Number(product?.myntra_rating || 0),
            reviews: 0,
            category: product?.article_type || product?.sub_category || product?.master_category || product?.brand_name || 'Sản phẩm',
            quantity: item.quantity,
          };
        }));
      })
      .catch((error) => console.error('Load cart API error:', error));
  }, [isAuthenticated]);

  useEffect(() => {
    if (!isAuthenticated || !user?.id) {
      setRecommendedProducts([]);
      return;
    }

    let isMounted = true;
    apiService.getRecommendations(user.id, 8)
      .then((items) => {
        if (isMounted) {
          setRecommendedProducts(
            items
              .map((item) => item.product_details)
              .filter((item): item is BackendProduct => Boolean(item))
              .map(toProduct)
          );
        }
      })
      .catch((error) => {
        console.error('Recommendations API error:', error);
        if (isMounted) {
          setRecommendedProducts([]);
        }
      });

    return () => {
      isMounted = false;
    };
  }, [isAuthenticated, user?.id]);

  const handleAddToCart = async (product: Product) => {
    try {
      await apiService.addToCart(product.id, 1);
    } catch (error) {
      console.error('Add to cart API error:', error);
    }

    setCartItems((prev) => {
      const existingItem = prev.find((item) => item.id === product.id);
      if (existingItem) {
        return prev.map((item) =>
          item.id === product.id
            ? { ...item, quantity: item.quantity + 1 }
            : item
        );
      }
      return [...prev, { ...product, quantity: 1 }];
    });
    setIsCartOpen(true);
  };

  const handleAddToWishlist = async (product: Product) => {
    try {
      await apiService.addToWishlist(product.id);
    } catch (error) {
      console.error('Add to wishlist API error:', error);
    }
  };

  const handleUpdateQuantity = async (id: string, quantity: number) => {
    try {
      await apiService.updateCartItem(id, quantity);
    } catch (error) {
      console.error('Update cart API error:', error);
    }
    setCartItems((prev) =>
      prev.map((item) => (item.id === id ? { ...item, quantity } : item))
    );
  };

  const handleRemoveItem = async (id: string) => {
    try {
      await apiService.removeCartItem(id);
    } catch (error) {
      console.error('Remove cart API error:', error);
    }
    setCartItems((prev) => prev.filter((item) => item.id !== id));
  };

  const handleCheckout = () => {
    setIsCartOpen(false);
    navigate('/checkout');
  };

  const handleCheckoutComplete = () => {
    setCartItems([]);
    navigate('/');
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Header
        cartItemCount={cartItems.reduce((sum, item) => sum + item.quantity, 0)}
        onCartClick={() => setIsCartOpen(true)}
      />

      <CartSidebar
        isOpen={isCartOpen}
        onClose={() => setIsCartOpen(false)}
        items={cartItems}
        onUpdateQuantity={handleUpdateQuantity}
        onRemoveItem={handleRemoveItem}
        onCheckout={handleCheckout}
      />

      {productsError && (
        <div className="container mx-auto px-4 pt-4">
          <div className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-red-700">
            Không kết nối được API sản phẩm: {productsError}
          </div>
        </div>
      )}

      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <HomePage
                products={productsLoading ? [] : products}
                recommendedProducts={recommendedProducts}
                onAddToCart={handleAddToCart}
                onAddToWishlist={handleAddToWishlist}
              />
            </ProtectedRoute>
          }
        />
        <Route
          path="/products"
          element={
            <ProtectedRoute>
              <ProductsPage products={productsLoading ? [] : products} onAddToCart={handleAddToCart} onAddToWishlist={handleAddToWishlist} />
            </ProtectedRoute>
          }
        />

        <Route
          path="/products/:id"
          element={
            <ProtectedRoute>
              <ProductDetailPage onAddToCart={handleAddToCart} onAddToWishlist={handleAddToWishlist} />
            </ProtectedRoute>
          }
        />
        <Route
          path="/wishlist"
          element={
            <ProtectedRoute>
              <WishlistPage onAddToCart={handleAddToCart} />
            </ProtectedRoute>
          }
        />
        <Route
          path="/orders"
          element={
            <ProtectedRoute>
              <OrdersPage />
            </ProtectedRoute>
          }
        />


        <Route
          path="/admin"
          element={
            <AdminRoute>
              <AdminPage />
            </AdminRoute>
          }
        />

        <Route
          path="/dashboard"
          element={
            <AdminRoute>
              <Dashboard />
            </AdminRoute>
          }
        />
        <Route
          path="/data-science"
          element={
            <AdminRoute>
              <DataScientistPage />
            </AdminRoute>
          }
        />
        <Route
          path="/checkout"
          element={
            <ProtectedRoute>
              <CheckoutPage items={cartItems} onComplete={handleCheckoutComplete} />
            </ProtectedRoute>
          }
        />
      </Routes>
    </div>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppContent />
      </AuthProvider>
    </BrowserRouter>
  );
}
