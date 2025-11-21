import React, { useState } from 'react';
import { Check, Download, Maximize2, Info, X } from 'lucide-react';
import type { Creative } from '@/types/creative';
import { API_BASE_URL } from '@/services/api';
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
  const [showDetails, setShowDetails] = useState(false);

  const handleDownload = (e: React.MouseEvent) => {
    e.stopPropagation();
    const link = document.createElement('a');
    link.href = `${API_BASE_URL}${creative.image_url}`;
    link.download = creative.image_filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div 
      className={`
        group relative rounded-xl overflow-hidden transition-all duration-300
        ${isSelected 
          ? 'ring-2 ring-primary shadow-[0_0_30px_rgba(0,166,81,0.3)] scale-[1.02]' 
          : 'hover:scale-[1.01] hover:ring-1 hover:ring-white/20'
        }
      `}
    >
      {/* Main Image Area */}
      <div 
        className="relative aspect-[16/10] cursor-pointer"
        onClick={onClick}
      >
        <img
          src={`${API_BASE_URL}${creative.image_url}`}
          alt={`Variant ${creative.variant_number}`}
          className="w-full h-full object-cover"
          loading="lazy"
        />
        
        {/* Gradient Overlay */}
        <div className="absolute inset-0 bg-gradient-to-t from-black/90 via-black/20 to-transparent opacity-80" />

        {/* Top Status Bar */}
        <div className="absolute top-3 left-3 right-3 flex justify-between items-start">
          <RecommendationBadge score={creative.recommendation_score} />
          
          {isSelected && (
            <div className="bg-primary text-white p-1.5 rounded-full shadow-lg shadow-primary/40 animate-in zoom-in duration-200">
              <Check className="w-4 h-4" strokeWidth={3} />
            </div>
          )}
        </div>

        {/* Hover Actions Overlay */}
        <div className="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity duration-300 bg-black/40 backdrop-blur-[2px]">
          <button 
            onClick={(e) => { e.stopPropagation(); onClick?.(); }}
            className="bg-white/10 hover:bg-white/20 text-white p-3 rounded-full backdrop-blur-md transition-all transform hover:scale-110 border border-white/20"
            title="View Fullscreen"
          >
            <Maximize2 className="w-6 h-6" />
          </button>
        </div>

        {/* Bottom Controls */}
        <div className="absolute bottom-0 left-0 right-0 p-4 flex items-end justify-between">
          <div>
            <h4 className="text-white font-bold text-sm uppercase tracking-wider mb-1">
              Variant {creative.variant_number}
            </h4>
            <button 
              onClick={(e) => { e.stopPropagation(); setShowDetails(!showDetails); }}
              className="flex items-center gap-1.5 text-xs text-zinc-400 hover:text-white transition-colors"
            >
              <Info className="w-3 h-3" />
              <span>Technical Analysis</span>
            </button>
          </div>

          <div className="flex gap-2">
            <button
              onClick={handleDownload}
              className="p-2 rounded-lg bg-white/5 hover:bg-white/10 text-white border border-white/10 transition-colors backdrop-blur-sm"
              title="Download Asset"
            >
              <Download className="w-4 h-4" />
            </button>
            <button
              onClick={(e) => { e.stopPropagation(); onSelect(); }}
              className={`
                px-4 py-2 rounded-lg font-medium text-sm transition-all backdrop-blur-sm
                ${isSelected 
                  ? 'bg-primary text-white shadow-[0_0_15px_rgba(0,166,81,0.4)]' 
                  : 'bg-white text-black hover:bg-white/90'
                }
              `}
            >
              {isSelected ? 'Active' : 'Select'}
            </button>
          </div>
        </div>
      </div>

      {/* Technical Details Drawer */}
      {showDetails && (
        <div className="absolute inset-0 bg-zinc-950/95 backdrop-blur-xl z-10 p-6 animate-in slide-in-from-bottom-10 duration-200">
          <div className="flex justify-between items-start mb-4">
            <h5 className="text-white font-bold text-sm uppercase tracking-wider flex items-center gap-2">
              <Info className="w-4 h-4 text-primary" />
              Analysis Data
            </h5>
            <button 
              onClick={(e) => { e.stopPropagation(); setShowDetails(false); }}
              className="text-zinc-500 hover:text-white transition-colors"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
          <p className="text-zinc-300 text-xs leading-relaxed font-mono">
            {creative.score_reasoning || "No specific reasoning data available for this variant."}
          </p>
          <div className="mt-6 pt-4 border-t border-white/10 grid grid-cols-2 gap-4">
            <div>
              <span className="text-[10px] uppercase text-zinc-500 block mb-1">Resolution</span>
              <span className="text-xs text-white font-mono">1024x1024</span>
            </div>
            <div>
              <span className="text-[10px] uppercase text-zinc-500 block mb-1">Format</span>
              <span className="text-xs text-white font-mono">WEBP</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
