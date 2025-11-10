import React, { useState } from 'react';
import type { Communication } from '/Users/asreenivas/Library/CloudStorage/OneDrive-StarHubLtd/02_Data_Analytics/Scripts/29. Customer Comms Generator/frontend/src/types/communication';
import type { Campaign } from '/Users/asreenivas/Library/CloudStorage/OneDrive-StarHubLtd/02_Data_Analytics/Scripts/29. Customer Comms Generator/frontend/src/types/campaign';
import { CommunicationCard } from '/Users/asreenivas/Library/CloudStorage/OneDrive-StarHubLtd/02_Data_Analytics/Scripts/29. Customer Comms Generator/frontend/src/components/ResultsDisplay/CommunicationCard';
import { EditModal } from '/Users/asreenivas/Library/CloudStorage/OneDrive-StarHubLtd/02_Data_Analytics/Scripts/29. Customer Comms Generator/frontend/src/components/ActionPanel/EditModal';
import { LoadingSpinner } from '/Users/asreenivas/Library/CloudStorage/OneDrive-StarHubLtd/02_Data_Analytics/Scripts/29. Customer Comms Generator/frontend/src/components/shared/LoadingSpinner';

interface ChatInterfaceProps {
  communications?: Communication[];
  campaign?: Campaign;
  loading?: boolean;
  onRefresh?: () => void;
}

export const ChatInterface: React.FC<ChatInterfaceProps> = ({
  communications = [],
  campaign,
  loading = false,
  onRefresh,
}) => {
  const [editingCommunication, setEditingCommunication] = useState<Communication | null>(null);

  // Sort communications by score (highest first)
  const sortedCommunications = [...communications].sort(
    (a, b) => b.recommendation_score - a.recommendation_score
  );

  if (loading) {
    return (
      <div className="card h-full flex flex-col items-center justify-center">
        <LoadingSpinner size="lg" />
        <p className="mt-4 text-gray-600">Generating communications...</p>
        <p className="text-sm text-gray-500">This may take 30-60 seconds</p>
      </div>
    );
  }

  if (communications.length === 0) {
    return (
      <div className="card h-full flex flex-col items-center justify-center text-center">
        <div className="text-6xl mb-4">💬</div>
        <h3 className="text-xl font-semibold text-gray-900 mb-2">
          No Communications Yet
        </h3>
        <p className="text-gray-600 max-w-md">
          Fill out the campaign form and click "Generate Communications" to create
          AI-powered marketing messages.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="card">
        <div className="flex justify-between items-center">
          <h2 className="text-xl font-bold">
            Generated Communications ({communications.length})
          </h2>
          {onRefresh && (
            <button
              onClick={onRefresh}
              className="text-primary-600 hover:text-primary-700 font-medium text-sm"
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

      {editingCommunication && (
        <EditModal
          communication={editingCommunication}
          channel={campaign?.channel || ''}
          onClose={() => setEditingCommunication(null)}
          onSave={onRefresh || (() => {})}
        />
      )}
    </div>
  );
};

export default ChatInterface;
