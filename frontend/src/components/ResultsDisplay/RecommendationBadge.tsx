import React from 'react';

interface RecommendationBadgeProps {
  score: number;
  isTop?: boolean;
}

export const RecommendationBadge: React.FC<RecommendationBadgeProps> = ({
  score,
  isTop = false,
}) => {
  const getScoreColor = (score: number) => {
    if (score >= 90) return 'bg-green-100 text-green-800 border-green-300';
    if (score >= 70) return 'bg-yellow-100 text-yellow-800 border-yellow-300';
    return 'bg-red-100 text-red-800 border-red-300';
  };

  return (
    <div className={`inline-flex items-center gap-2 px-3 py-1 rounded-full border-2 font-semibold ${getScoreColor(score)}`}>
      {isTop && <span className="text-lg">👑</span>}
      <span>Score: {score}/100</span>
    </div>
  );
};
