import React, { useState } from 'react';
import type { Creative } from '../types/creative';
import type { Campaign } from '../types/campaign';
import { CreativeCard } from './CreativeCard';
import { Button } from './shared/Button';
import { LoadingSpinner } from './shared/LoadingSpinner';
import { ImageViewerModal } from './shared/ImageViewerModal';
import { creativeAPI } from '../services/api';

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
      <div className="card text-center p-6">
        <div className="text-4xl mb-2">⚠️</div>
        <p className="text-gray-600 mb-4">{error}</p>
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
      <div className="card text-center p-6">
        <div role="status" aria-live="polite">
          <LoadingSpinner size="md" />
          <p className="text-gray-600 mt-4">
            Generating creative images... (3-5 seconds)
          </p>
          <span className="sr-only">Generating creative images, please wait</span>
        </div>
      </div>
    );
  }

  // Empty State
  if (creatives.length === 0) {
    const channel = campaign?.channel?.toLowerCase() || '';
    const supportsCreatives = channel === 'email' || channel === 'push' || channel.includes('email') || channel.includes('push');
    
    return (
      <div className="card text-center p-6">
        <h3 className="text-lg font-semibold mb-2">Campaign Creatives</h3>
        {supportsCreatives ? (
          <>
            <p className="text-gray-600 mb-4">
              Generate AI-powered creative images for your campaign
            </p>
            {onGenerate && (
              <Button onClick={onGenerate} variant="primary" className="py-3 px-6 text-lg">
                🎨 Generate Creative Images
              </Button>
            )}
          </>
        ) : (
          <p className="text-gray-600">
            Creative images are only available for Email and Push Notification campaigns.
            Current channel: <strong>{campaign?.channel || 'Unknown'}</strong>
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
      <div className="card">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-semibold">Campaign Creatives</h3>
          <div className="flex gap-2">
            {onGenerate && (
              <Button onClick={onGenerate} variant="primary" className="text-sm py-2 px-4">
                🎨 Generate New Creatives
              </Button>
            )}
            {onRefresh && (
              <Button onClick={onRefresh} variant="secondary" className="text-sm py-2 px-3">
                🔄 Refresh
              </Button>
            )}
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
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
