import React from 'react';
import type { Creative } from '../types/creative';
import { Button } from './shared/Button';
import { RecommendationBadge } from './ResultsDisplay/RecommendationBadge';

interface CreativeCardProps {
  creative: Creative;
  isSelected: boolean;
  onSelect: () => void;
  onClick?: () => void;
}

export const CreativeCard: React.FC<CreativeCardProps> = ({
  creative,
  isSelected,
  onSelect,
  onClick,
}) => {
  const handleDownload = () => {
    const link = document.createElement('a');
    link.href = `http://localhost:8000${creative.image_url}`;
    link.download = creative.image_filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      onSelect();
    }
  };

  return (
    <div className={`card ${isSelected ? 'border-2 border-primary-500 shadow-glow' : ''}`}>
      {/* Image Preview - Clickable to view full size */}
      <div 
        className="relative cursor-pointer group" 
        onClick={onClick}
        role="button"
        tabIndex={0}
        onKeyDown={(e) => {
          if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            onClick?.();
          }
        }}
        aria-label={`View full size image of variant ${creative.variant_number}`}
      >
        <img
          src={`http://localhost:8000${creative.image_url}`}
          alt={`Creative variant ${creative.variant_number}, recommendation score ${creative.recommendation_score} out of 100`}
          className="w-full h-auto rounded-t transition-opacity group-hover:opacity-90"
          loading="lazy"
          role="img"
        />
        {/* Hover overlay */}
        <div className="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity bg-slate-950 bg-opacity-60 rounded-t backdrop-blur-sm">
          <div className="bg-slate-800 text-slate-100 px-3 py-2 rounded-lg font-semibold text-sm border border-slate-600">
            🔍 Click to view full size
          </div>
        </div>
      </div>

      {/* Header Section */}
      <div className="flex justify-between items-center p-3">
        <RecommendationBadge score={creative.recommendation_score} />
        <span className="text-sm font-semibold text-slate-300">
          Variant {creative.variant_number}
        </span>
      </div>

      {/* Actions Section */}
      <div className="flex gap-2 p-3 pt-0">
        <Button
          onClick={onSelect}
          onKeyDown={handleKeyPress}
          variant={isSelected ? 'primary' : 'secondary'}
          className="flex-1 text-xs py-1"
          aria-label={`Select variant ${creative.variant_number}`}
          aria-pressed={isSelected}
        >
          {isSelected ? '✓ Selected' : 'Select'}
        </Button>
        <Button
          onClick={handleDownload}
          variant="secondary"
          className="text-xs py-1"
          aria-label={`Download variant ${creative.variant_number}`}
        >
          ⬇ Download
        </Button>
      </div>

      {/* Score Reasoning */}
      <details className="px-3 pb-3">
        <summary className="cursor-pointer text-sm font-medium text-slate-300 hover:text-slate-100 transition-colors">
          Score Details
        </summary>
        <p className="text-xs text-slate-400 mt-2 leading-relaxed">
          {creative.score_reasoning}
        </p>
      </details>
    </div>
  );
};
