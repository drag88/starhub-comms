import React, { useState } from 'react';
import type { Communication } from '../../types/communication';
import type { Campaign } from '../../types/campaign';
import type { Creative } from '../../types/creative';
import { CommunicationCard } from './CommunicationCard';
import { CreativeCard } from '../CreativeCard';
import { EditModal } from '../ActionPanel/EditModal';
import { ImageViewerModal } from '../shared/ImageViewerModal';
import { LoadingSpinner } from '../shared/LoadingSpinner';
import { Button } from '../shared/Button';

interface UnifiedResultsProps {
  communications?: Communication[];
  creatives?: Creative[];
  campaign?: Campaign;
  communicationsLoading?: boolean;
  creativesLoading?: boolean;
  canGenerateCreatives?: boolean;
  onRefreshCommunications?: () => void;
  onGenerateCreatives?: () => void;
  onRefreshCreatives?: () => void;
  onSelectCreative?: (creativeId: number) => void;
}

export const UnifiedResults: React.FC<UnifiedResultsProps> = ({
  communications = [],
  creatives = [],
  campaign,
  communicationsLoading = false,
  creativesLoading = false,
  canGenerateCreatives = false,
  onRefreshCommunications,
  onGenerateCreatives,
  onRefreshCreatives,
  onSelectCreative,
}) => {
  const [editingCommunication, setEditingCommunication] = useState<Communication | null>(null);
  const [modalOpen, setModalOpen] = useState(false);
  const [modalInitialIndex, setModalInitialIndex] = useState(0);

  // Sort communications and creatives by score
  const sortedCommunications = [...communications].sort(
    (a, b) => b.recommendation_score - a.recommendation_score
  );
  const sortedCreatives = [...creatives].sort(
    (a, b) => b.recommendation_score - a.recommendation_score
  );

  const handleOpenModal = (index: number) => {
    setModalInitialIndex(index);
    setModalOpen(true);
  };

  // Loading state
  if (communicationsLoading && communications.length === 0) {
    return (
      <div className="card h-full flex flex-col items-center justify-center">
        <LoadingSpinner size="lg" />
        <p className="mt-4 text-slate-400">Generating communications...</p>
        <p className="text-sm text-slate-500">This may take 30-60 seconds</p>
      </div>
    );
  }

  // Empty state
  if (communications.length === 0) {
    return (
      <div className="card h-full flex flex-col items-center justify-center text-center">
        <div className="text-6xl mb-4">💬</div>
        <h3 className="text-xl font-semibold text-slate-100 mb-2">
          No Communications Yet
        </h3>
        <p className="text-slate-400 max-w-md">
          Fill out the campaign form and click "Generate Communications" to create
          AI-powered marketing messages.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Communications Section */}
      <div className="card">
        <div className="flex justify-between items-center">
          <h2 className="text-xl font-bold text-slate-100">
            Generated Communications ({communications.length})
          </h2>
          {onRefreshCommunications && (
            <button
              onClick={onRefreshCommunications}
              className="text-primary-400 hover:text-primary-300 font-medium text-sm transition-colors"
            >
              🔄 Regenerate
            </button>
          )}
        </div>
      </div>

      {sortedCommunications.map((communication, index) => (
        <CommunicationCard
          key={communication.communication_id}
          communication={communication}
          campaign={campaign}
          isTop={index === 0}
          onEdit={setEditingCommunication}
        />
      ))}

      {/* Creative Images Section */}
      {canGenerateCreatives && (
        <div className="card">
          <div className="flex justify-between items-center mb-4">
            <div>
              <h2 className="text-xl font-bold text-slate-100">Campaign Creatives</h2>
              <p className="text-sm text-slate-400 mt-1">
                Generate AI-powered creative images for your campaign
              </p>
            </div>
            <div className="flex gap-2">
              {creatives.length > 0 && onRefreshCreatives && (
                <Button onClick={onRefreshCreatives} variant="secondary" className="text-sm py-2 px-3">
                  🔄 Refresh
                </Button>
              )}
              {onGenerateCreatives && (
                <Button onClick={onGenerateCreatives} variant="primary" className="text-sm py-2 px-4">
                  {creatives.length > 0 ? '🎨 Regenerate' : '🎨 Generate Creative Images'}
                </Button>
              )}
            </div>
          </div>

          {/* Creative Loading */}
          {creativesLoading && (
            <div className="text-center py-8">
              <LoadingSpinner size="md" />
              <p className="text-slate-400 mt-4">
                Generating creative images... (3-5 seconds)
              </p>
            </div>
          )}

          {/* Creative Results */}
          {!creativesLoading && creatives.length > 0 && (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {sortedCreatives.map((creative, index) => (
                <CreativeCard
                  key={creative.creative_id}
                  creative={creative}
                  isSelected={creative.is_selected}
                  onSelect={() => onSelectCreative?.(creative.creative_id)}
                  onClick={() => handleOpenModal(index)}
                />
              ))}
            </div>
          )}

          {/* Empty Creative State */}
          {!creativesLoading && creatives.length === 0 && (
            <div className="text-center py-8 text-slate-500">
              <div className="text-4xl mb-2">🎨</div>
              <p>No creative images generated yet</p>
              <p className="text-sm mt-1">Click the button above to generate</p>
            </div>
          )}
        </div>
      )}

      {/* Edit Modal */}
      {editingCommunication && (
        <EditModal
          communication={editingCommunication}
          channel={campaign?.channel || ''}
          onClose={() => setEditingCommunication(null)}
          onSave={onRefreshCommunications || (() => {})}
        />
      )}

      {/* Image Viewer Modal */}
      <ImageViewerModal
        creatives={sortedCreatives}
        initialIndex={modalInitialIndex}
        isOpen={modalOpen}
        onClose={() => setModalOpen(false)}
      />
    </div>
  );
};

export default UnifiedResults;

