import { useState } from 'react';
import { Brain, Image, Play, Target, TrendingUp } from 'lucide-react';
import { apiService } from '@/services/api';
import originalMissingValue from '../../../../data_scientist/reports/v_20260506_193346/original/3_1_2_missing_value_analysis.png';
import originalCategoryCounts from '../../../../data_scientist/reports/v_20260506_193346/original/3_1_3_category_distribution_counts.png';
import originalCategoryHeatmap from '../../../../data_scientist/reports/v_20260506_193346/original/3_1_3_category_distribution_heatmap.png';
import originalAttributeVariance from '../../../../data_scientist/reports/v_20260506_193346/original/3_1_4_attribute_variance.png';
import originalPriceBoxplot from '../../../../data_scientist/reports/v_20260506_193346/original/3_1_5_price_analysis_boxplot.png';
import originalPriceDistribution from '../../../../data_scientist/reports/v_20260506_193346/original/3_1_5_price_analysis_dist.png';
import originalRatingInsights from '../../../../data_scientist/reports/v_20260506_193346/original/3_1_6_rating_insights.png';
import originalTextLength from '../../../../data_scientist/reports/v_20260506_193346/original/3_1_7_text_semantic_len.png';
import originalBrandDominance from '../../../../data_scientist/reports/v_20260506_193346/original/3_1_8_brand_dominance.png';
import normalizedPriceDistribution from '../../../../data_scientist/reports/v_20260506_193346/normalized/3_3_2_price_distribution_comparison.png';
import normalizedDeduplicationImpact from '../../../../data_scientist/reports/v_20260506_193346/normalized/3_3_3_deduplication_impact.png';
import normalizedLabelDiversity from '../../../../data_scientist/reports/v_20260506_193346/normalized/3_3_4_label_diversity_plot.png';
import normalizedOnehotSparsity from '../../../../data_scientist/reports/v_20260506_193346/normalized/3_3_5_onehot_sparsity.png';
import normalizedTextShrinkage from '../../../../data_scientist/reports/v_20260506_193346/normalized/3_3_6_text_shrinkage.png';
import normalizedFeatureCorrelation from '../../../../data_scientist/reports/v_20260506_193346/normalized/3_3_7_feature_correlation.png';
import normalizedPostScalingBoxplot from '../../../../data_scientist/reports/v_20260506_193346/normalized/3_3_9_post_scaling_boxplot.png';
import normalizedGnnReadiness from '../../../../data_scientist/reports/v_20260506_193346/normalized/3_3_10_gnn_readiness.png';

const insights = [
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

const originalReportImages = [
  { title: 'Missing Value Analysis', src: originalMissingValue },
  { title: 'Category Distribution Counts', src: originalCategoryCounts },
  { title: 'Category Distribution Heatmap', src: originalCategoryHeatmap },
  { title: 'Attribute Variance', src: originalAttributeVariance },
  { title: 'Price Analysis Boxplot', src: originalPriceBoxplot },
  { title: 'Price Analysis Distribution', src: originalPriceDistribution },
  { title: 'Rating Insights', src: originalRatingInsights },
  { title: 'Text Semantic Length', src: originalTextLength },
  { title: 'Brand Dominance', src: originalBrandDominance },
];

const normalizedReportImages = [
  { title: 'Price Distribution Comparison', src: normalizedPriceDistribution },
  { title: 'Deduplication Impact', src: normalizedDeduplicationImpact },
  { title: 'Label Diversity', src: normalizedLabelDiversity },
  { title: 'One-hot Sparsity', src: normalizedOnehotSparsity },
  { title: 'Text Shrinkage', src: normalizedTextShrinkage },
  { title: 'Feature Correlation', src: normalizedFeatureCorrelation },
  { title: 'Post Scaling Boxplot', src: normalizedPostScalingBoxplot },
  { title: 'GNN Readiness', src: normalizedGnnReadiness },
];

function ReportImagePanel({ title, images }: { title: string; images: Array<{ title: string; src: string }> }) {
  const [failedImages, setFailedImages] = useState<Record<string, boolean>>({});

  return (
    <div className="rounded-lg bg-white p-5 shadow-sm">
      <div className="mb-4 flex items-center gap-2">
        <Image className="h-5 w-5 text-blue-600" />
        <h2 className="text-lg font-bold">{title}</h2>
      </div>
      <div className="space-y-4">
        {images.map((item) => (
          <figure key={item.src} className="overflow-hidden rounded-lg border bg-gray-50">
            <figcaption className="border-b bg-white px-3 py-2 text-sm font-semibold">{item.title}</figcaption>
            {failedImages[item.src] ? (
              <div className="flex min-h-40 items-center justify-center p-4 text-center text-sm text-gray-500">
                Không tải được ảnh: {item.title}
              </div>
            ) : (
              <img
                src={item.src}
                alt={item.title}
                className="block h-auto w-full"
                loading="lazy"
                onError={() => setFailedImages((current) => ({ ...current, [item.src]: true }))}
              />
            )}
          </figure>
        ))}
      </div>
    </div>
  );
}

export function DataScientistPage() {
  const [training, setTraining] = useState(false);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  const triggerTraining = async () => {
    setTraining(true);
    setError('');
    setMessage('');
    try {
      const response = await apiService.triggerAITraining();
      setMessage(response.message);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Không kích hoạt được training');
    } finally {
      setTraining(false);
    }
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8 flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <Brain className="w-8 h-8 text-purple-600" />
          <h1 className="text-3xl font-bold">Data Science & Analytics</h1>
        </div>
        <div className="flex gap-2">
          <button onClick={triggerTraining} disabled={training} className="flex items-center gap-2 rounded-lg bg-purple-600 px-4 py-2 text-white hover:bg-purple-700 disabled:opacity-60">
            <Play className="h-4 w-4" />
            {training ? 'Đang kích hoạt...' : 'Train AI'}
          </button>
        </div>
      </div>

      {message && <div className="mb-4 rounded-lg bg-green-50 p-3 text-green-700">{message}</div>}
      {error && <div className="mb-4 rounded-lg bg-red-50 p-3 text-red-700">{error}</div>}

      <div className="mb-8 grid grid-cols-1 gap-6 lg:grid-cols-2">
        <ReportImagePanel title="Original" images={originalReportImages} />
        <ReportImagePanel title="Normalized" images={normalizedReportImages} />
      </div>

      {/* AI Insights */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
        {insights.map((insight, index) => (
          <div key={index} className="bg-white rounded-lg shadow-sm p-6 hover:shadow-md transition-shadow">
            <insight.icon className={`w-8 h-8 mb-3 ${insight.color}`} />
            <h3 className="font-bold mb-2">{insight.title}</h3>
            <p className="text-sm text-gray-600">{insight.description}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
