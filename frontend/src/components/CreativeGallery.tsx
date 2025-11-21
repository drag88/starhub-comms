import React, { useState } from 'react';
import { Image, RotateCcw, Sparkles, AlertCircle } from 'lucide-react';
import type { Creative } from '@/types/creative';
import type { Campaign } from '@/types/campaign';
import { CreativeCard } from './CreativeCard';
import { Button } from './shared/Button';
import { LoadingSpinner } from './shared/LoadingSpinner';
import { ImageViewerModal } from './shared/ImageViewerModal';
import { creativeAPI } from '@/services/api';

interface CreativeGalleryProps {
  creatives: Creative[];
  campaign?: Campaign;
  loading?: boolean;
  onGenerate?: () => void;
  onRefresh?: () => void;
}

export const CreativeGallery: React.FC<CreativeGalleryProps> = ({
  creatives,
  campaign,
  loading = false,
  onGenerate,
  onRefresh,
}) => {
  const [selectedId, setSelectedId] = useState<number | null>(
    creatives.find(c => c.is_selected)?.creative_id || null
  );
  const [error, setError] = useState<string | null>(null);
  const [modalOpen, setModalOpen] = useState(false);
  const [modalInitialIndex, setModalInitialIndex] = useState(0);

  const handleSelect = async (creativeId: number) => {
    try {
      // Deselect previous if different
      if (selectedId && selectedId !== creativeId) {
        await creativeAPI.select(selectedId, false);
      }

      // Toggle current
      const isCurrentlySelected = selectedId === creativeId;
      await creativeAPI.select(creativeId, !isCurrentlySelected);
      setSelectedId(isCurrentlySelected ? null : creativeId);

      // Refresh data
      if (onRefresh) onRefresh();
    } catch (error) {
      console.error('Selection failed:', error);
      setError('Failed to update selection. Please try again.');
      // Revert to previous state
      if (onRefresh) onRefresh();
    }
  };

  // Error state
  if (error) {
    return (
      <div className="glass-panel p-8 text-center rounded-xl">
        <div className="flex justify-center mb-4">
          <div className="p-3 rounded-full bg-red-500/10">
            <AlertCircle className="w-8 h-8 text-red-400" />
          </div>
        </div>
        <p className="text-zinc-300 mb-6">{error}</p>
        <Button
          onClick={() => {
            setError(null);
            if (onGenerate) onGenerate();
          }}
          variant="primary"
        >
          Try Again
        </Button>
      </div>
    );
  }

  // Loading State
  if (loading) {
    return (
      <div className="glass-panel p-12 text-center rounded-xl">
        <div role="status" aria-live="polite" className="flex flex-col items-center">
          <LoadingSpinner size="md" />
          <p className="text-zinc-400 mt-6 animate-pulse font-medium uppercase tracking-widest text-xs">
            Generating creative assets...
          </p>
        </div>
      </div>
    );
  }

  // Empty State
  if (creatives.length === 0) {
    const channel = campaign?.channel?.toLowerCase() || '';
    const supportsCreatives = channel === 'email' || channel === 'push' || channel.includes('email') || channel.includes('push');
    
    return (
      <div className="glass-panel p-12 text-center rounded-xl border-dashed border-2 border-zinc-800/50">
        <div className="flex justify-center mb-4">
          <div className="p-4 rounded-full bg-zinc-900 border border-zinc-800">
            <Image className="w-8 h-8 text-zinc-600" />
          </div>
        </div>
        <h3 className="text-lg font-bold text-white uppercase tracking-wide mb-2">Campaign Creatives</h3>
        {supportsCreatives ? (
          <>
            <p className="text-zinc-400 mb-6 max-w-md mx-auto">
              Generate AI-powered creative images optimized for your {campaign?.channel || 'campaign'} channel.
            </p>
            {onGenerate && (
              <Button onClick={onGenerate} variant="primary" className="mx-auto">
                <Sparkles className="w-4 h-4" />
                Generate Visual Assets
              </Button>
            )}
          </>
        ) : (
          <p className="text-zinc-500 max-w-md mx-auto">
            Creative image generation is currently available for Email and Push Notification channels only.
          </p>
        )}
      </div>
    );
  }

  const handleOpenModal = (index: number) => {
    setModalInitialIndex(index);
    setModalOpen(true);
  };

  const sortedCreatives = [...creatives].sort((a, b) => b.recommendation_score - a.recommendation_score);

  // Results State
  return (
    <>
      <div className="glass-panel p-6 rounded-xl">
        <div className="flex justify-between items-center mb-6 pb-6 border-b border-white/5">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded bg-primary/10 border border-primary/20">
              <Image className="w-5 h-5 text-primary" />
            </div>
            <h3 className="text-sm font-bold text-white uppercase tracking-widest">
              Generated Creatives
            </h3>
          </div>
          <div className="flex gap-3">
            {onGenerate && (
              <Button onClick={onGenerate} variant="primary" className="text-xs px-4">
                <Sparkles className="w-3 h-3" />
                Generate New
              </Button>
            )}
            {onRefresh && (
              <Button onClick={onRefresh} variant="secondary" className="text-xs px-3">
                <RotateCcw className="w-3 h-3" />
              </Button>
            )}
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {sortedCreatives.map((creative, index) => (
            <CreativeCard
              key={creative.creative_id}
              creative={creative}
              isSelected={creative.creative_id === selectedId}
              onSelect={() => handleSelect(creative.creative_id)}
              onClick={() => handleOpenModal(index)}
            />
          ))}
        </div>
      </div>

      {/* Image Viewer Modal */}
      <ImageViewerModal
        creatives={sortedCreatives}
        initialIndex={modalInitialIndex}
        isOpen={modalOpen}
        onClose={() => setModalOpen(false)}
      />
    </>
  );
};

export default CreativeGallery;
