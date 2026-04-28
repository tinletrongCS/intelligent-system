import { BarChart, Bar, LineChart, Line, ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar } from 'recharts';
import { Brain, TrendingUp, Users, Target, Activity } from 'lucide-react';

const customerBehavior = [
  { hour: '0h', visits: 45, purchases: 12 },
  { hour: '4h', visits: 23, purchases: 5 },
  { hour: '8h', visits: 234, purchases: 67 },
  { hour: '12h', visits: 456, purchases: 123 },
  { hour: '16h', visits: 389, purchases: 98 },
  { hour: '20h', visits: 567, purchases: 145 },
];

const customerSegmentation = [
  { price: 5000000, quantity: 234, category: 'Budget' },
  { price: 15000000, quantity: 456, category: 'Mid-range' },
  { price: 25000000, quantity: 189, category: 'Mid-range' },
  { price: 35000000, quantity: 123, category: 'Premium' },
  { price: 45000000, quantity: 67, category: 'Premium' },
  { price: 55000000, quantity: 34, category: 'Luxury' },
];

const productPerformance = [
  { category: 'Chất lượng', A: 85, B: 78, fullMark: 100 },
  { category: 'Giá cả', A: 72, B: 88, fullMark: 100 },
  { category: 'Đánh giá', A: 90, B: 82, fullMark: 100 },
  { category: 'Độ phổ biến', A: 88, B: 75, fullMark: 100 },
  { category: 'Tồn kho', A: 65, B: 92, fullMark: 100 },
];

const conversionFunnel = [
  { stage: 'Truy cập', users: 10000, rate: 100 },
  { stage: 'Xem sản phẩm', users: 6500, rate: 65 },
  { stage: 'Thêm giỏ hàng', users: 3200, rate: 32 },
  { stage: 'Thanh toán', users: 1800, rate: 18 },
  { stage: 'Hoàn tất', users: 1200, rate: 12 },
];

const predictions = [
  { metric: 'Doanh thu dự kiến tháng sau', value: '950M₫', confidence: 87 },
  { metric: 'Khách hàng mới', value: '~340', confidence: 82 },
  { metric: 'Tỷ lệ churn', value: '3.2%', confidence: 79 },
  { metric: 'Giá trị đơn hàng TB', value: '1.8M₫', confidence: 91 },
];

const insights = [
  {
    title: 'Giờ vàng mua sắm',
    description: 'Khách hàng mua sắm nhiều nhất vào khung giờ 20h-22h với tỷ lệ chuyển đổi cao nhất.',
    icon: Activity,
    color: 'text-blue-600',
  },
  {
    title: 'Phân khúc khách hàng',
    description: 'Phân khúc Mid-range chiếm 45% doanh thu, cần tập trung marketing vào segment này.',
    icon: Users,
    color: 'text-purple-600',
  },
  {
    title: 'Xu hướng sản phẩm',
    description: 'Sản phẩm Apple có tỷ lệ đánh giá cao nhất (4.8/5) và độ trung thành khách hàng tốt.',
    icon: TrendingUp,
    color: 'text-green-600',
  },
  {
    title: 'Tối ưu hóa chuyển đổi',
    description: 'Giảm 45% tỷ lệ bỏ giỏ hàng bằng cách thêm khuyến mãi miễn phí vận chuyển.',
    icon: Target,
    color: 'text-orange-600',
  },
];

export function DataScientistPage() {
  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex items-center gap-3 mb-8">
        <Brain className="w-8 h-8 text-purple-600" />
        <h1 className="text-3xl font-bold">Data Science & Analytics</h1>
      </div>

      {/* AI Insights */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {insights.map((insight, index) => (
          <div key={index} className="bg-white rounded-lg shadow-sm p-6 hover:shadow-md transition-shadow">
            <insight.icon className={`w-8 h-8 mb-3 ${insight.color}`} />
            <h3 className="font-bold mb-2">{insight.title}</h3>
            <p className="text-sm text-gray-600">{insight.description}</p>
          </div>
        ))}
      </div>

      {/* Predictions */}
      <div className="bg-gradient-to-r from-purple-600 to-blue-600 rounded-lg shadow-sm p-6 mb-8">
        <h2 className="text-2xl font-bold text-white mb-6">Dự đoán bằng AI/ML</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {predictions.map((pred, index) => (
            <div key={index} className="bg-white/10 backdrop-blur-sm rounded-lg p-4">
              <p className="text-white/80 text-sm mb-1">{pred.metric}</p>
              <p className="text-2xl font-bold text-white mb-2">{pred.value}</p>
              <div className="flex items-center gap-2">
                <div className="flex-1 bg-white/20 rounded-full h-2">
                  <div
                    className="bg-white rounded-full h-2 transition-all"
                    style={{ width: `${pred.confidence}%` }}
                  />
                </div>
                <span className="text-white/80 text-sm">{pred.confidence}%</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        {/* Customer Behavior */}
        <div className="bg-white rounded-lg shadow-sm p-6">
          <h2 className="text-xl font-bold mb-4">Hành vi khách hàng theo giờ</h2>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={customerBehavior}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="hour" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="visits" stroke="#3b82f6" strokeWidth={2} name="Lượt truy cập" />
              <Line type="monotone" dataKey="purchases" stroke="#10b981" strokeWidth={2} name="Mua hàng" />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Conversion Funnel */}
        <div className="bg-white rounded-lg shadow-sm p-6">
          <h2 className="text-xl font-bold mb-4">Phễu chuyển đổi</h2>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={conversionFunnel} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis type="number" />
              <YAxis dataKey="stage" type="category" width={120} />
              <Tooltip />
              <Legend />
              <Bar dataKey="users" fill="#8b5cf6" name="Số người dùng" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Customer Segmentation */}
        <div className="bg-white rounded-lg shadow-sm p-6">
          <h2 className="text-xl font-bold mb-4">Phân khúc khách hàng (Giá vs Số lượng)</h2>
          <ResponsiveContainer width="100%" height={300}>
            <ScatterChart>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="price" name="Giá" unit="₫" />
              <YAxis dataKey="quantity" name="Số lượng" />
              <Tooltip cursor={{ strokeDasharray: '3 3' }} />
              <Legend />
              <Scatter name="Budget" data={customerSegmentation.filter(d => d.category === 'Budget')} fill="#10b981" />
              <Scatter name="Mid-range" data={customerSegmentation.filter(d => d.category === 'Mid-range')} fill="#3b82f6" />
              <Scatter name="Premium" data={customerSegmentation.filter(d => d.category === 'Premium')} fill="#8b5cf6" />
              <Scatter name="Luxury" data={customerSegmentation.filter(d => d.category === 'Luxury')} fill="#f59e0b" />
            </ScatterChart>
          </ResponsiveContainer>
        </div>

        {/* Product Performance Radar */}
        <div className="bg-white rounded-lg shadow-sm p-6">
          <h2 className="text-xl font-bold mb-4">So sánh hiệu suất sản phẩm</h2>
          <ResponsiveContainer width="100%" height={300}>
            <RadarChart data={productPerformance}>
              <PolarGrid />
              <PolarAngleAxis dataKey="category" />
              <PolarRadiusAxis angle={90} domain={[0, 100]} />
              <Radar name="iPhone 15 Pro" dataKey="A" stroke="#3b82f6" fill="#3b82f6" fillOpacity={0.6} />
              <Radar name="Samsung S24" dataKey="B" stroke="#ec4899" fill="#ec4899" fillOpacity={0.6} />
              <Legend />
              <Tooltip />
            </RadarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
