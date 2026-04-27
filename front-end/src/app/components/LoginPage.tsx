import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { ShieldCheck, User } from 'lucide-react';
import { useAuth } from '@/context/AuthContext';
import { Button } from '@/app/components/ui/button';
import { Input } from '@/app/components/ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/app/components/ui/card';
import { Alert, AlertDescription } from '@/app/components/ui/alert';

export const LoginPage: React.FC = () => {
  const [mode, setMode] = useState<'guest' | 'admin'>('guest');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [localError, setLocalError] = useState('');
  const { login, error, clearError, user } = useAuth();
  const navigate = useNavigate();

  const selectMode = (nextMode: 'guest' | 'admin') => {
    setMode(nextMode);
    setLocalError('');
    clearError();
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setLocalError('');
    clearError();

    try {
      await login(username, password);
      const savedUser = JSON.parse(localStorage.getItem('current_user') || '{}');
      const roleId = Number(savedUser.role_id || user?.role_id || 0);
      if (mode === 'admin' && roleId !== 3) {
        setLocalError('Tài khoản này không có quyền admin.');
        return;
      }
      navigate(mode === 'admin' ? '/admin' : '/');
    } catch (err) {
      console.error('Login error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <Card className="w-full max-w-md">
        <CardHeader className="space-y-2">
          <CardTitle className="text-2xl font-bold">Đăng Nhập</CardTitle>
          <CardDescription>Chọn loại đăng nhập trước khi vào hệ thống</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="mb-4 grid grid-cols-2 gap-2 rounded-lg bg-gray-100 p-1">
            <button type="button" onClick={() => selectMode('guest')} className={`flex items-center justify-center gap-2 rounded-md px-3 py-2 text-sm font-medium ${mode === 'guest' ? 'bg-white text-blue-600 shadow-sm' : 'text-gray-600'}`}>
              <User className="h-4 w-4" /> Guest
            </button>
            <button type="button" onClick={() => selectMode('admin')} className={`flex items-center justify-center gap-2 rounded-md px-3 py-2 text-sm font-medium ${mode === 'admin' ? 'bg-white text-blue-600 shadow-sm' : 'text-gray-600'}`}>
              <ShieldCheck className="h-4 w-4" /> Admin
            </button>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            {(error || localError) && (
              <Alert variant="destructive">
                <AlertDescription>{localError || error}</AlertDescription>
              </Alert>
            )}

            <div className="space-y-2">
              <label htmlFor="username" className="text-sm font-medium">Tên Đăng Nhập</label>
              <Input id="username" type="text" placeholder="Nhập tên đăng nhập" value={username} onChange={(e) => setUsername(e.target.value)} disabled={isLoading} required />
            </div>

            <div className="space-y-2">
              <label htmlFor="password" className="text-sm font-medium">Mật Khẩu</label>
              <Input id="password" type="password" placeholder="Nhập mật khẩu" value={password} onChange={(e) => setPassword(e.target.value)} disabled={isLoading} required />
            </div>


            <Button type="submit" className="w-full" disabled={isLoading}>{isLoading ? 'Đang đăng nhập...' : `Đăng Nhập ${mode === 'admin' ? 'Admin' : 'Guest'}`}</Button>

            <div className="text-center text-sm">
              <span className="text-gray-600">Chưa có tài khoản? </span>
              <Link to="/register" className="text-blue-600 hover:text-blue-700 font-medium">Đăng ký ngay</Link>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  );
};
