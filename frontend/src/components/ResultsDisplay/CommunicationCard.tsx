import React, { useState } from 'react';
import type { Communication } from '/Users/asreenivas/Library/CloudStorage/OneDrive-StarHubLtd/02_Data_Analytics/Scripts/29. Customer Comms Generator/frontend/src/types/communication';
import type { Campaign } from '/Users/asreenivas/Library/CloudStorage/OneDrive-StarHubLtd/02_Data_Analytics/Scripts/29. Customer Comms Generator/frontend/src/types/campaign';
import { RecommendationBadge } from '/Users/asreenivas/Library/CloudStorage/OneDrive-StarHubLtd/02_Data_Analytics/Scripts/29. Customer Comms Generator/frontend/src/components/ResultsDisplay/RecommendationBadge';
import { ScoreBreakdown } from '/Users/asreenivas/Library/CloudStorage/OneDrive-StarHubLtd/02_Data_Analytics/Scripts/29. Customer Comms Generator/frontend/src/components/ResultsDisplay/ScoreBreakdown';
import { exportCommunication } from '/Users/asreenivas/Library/CloudStorage/OneDrive-StarHubLtd/02_Data_Analytics/Scripts/29. Customer Comms Generator/frontend/src/services/export';
import { communicationAPI } from '/Users/asreenivas/Library/CloudStorage/OneDrive-StarHubLtd/02_Data_Analytics/Scripts/29. Customer Comms Generator/frontend/src/services/api';

interface CommunicationCardProps {
  communication: Communication;
  campaign?: Campaign;
  isTop: boolean;
  onEdit: (communication: Communication) => void;
}

export const CommunicationCard: React.FC<CommunicationCardProps> = ({
  communication,
  campaign,
  isTop,
  onEdit,
}) => {
  const [copied, setCopied] = useState(false);
  const [selected, setSelected] = useState(communication.is_selected);
  const [expanded, setExpanded] = useState(false);

  const text = communication.edited_text || communication.communication_text;

  const handleCopy = () => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleSelect = async () => {
    try {
      await communicationAPI.update(communication.communication_id, {
        is_selected: !selected,
      });
      setSelected(!selected);
    } catch (error) {
      console.error('Failed to update selection:', error);
    }
  };

  return (
    <div className={`card ${isTop ? 'border-2 border-green-500' : ''}`}>
      {/* Header */}
      <div className="flex justify-between items-center mb-3">
        <div className="flex items-center gap-2">
          <span className="text-sm font-semibold text-gray-700">
            Variation {communication.variation_number}
          </span>
          <RecommendationBadge score={communication.recommendation_score} isTop={isTop} />
        </div>
        <div className="flex items-center gap-2">
          {selected && (
            <span className="px-2 py-0.5 bg-green-100 text-green-700 text-xs rounded font-medium">
              Selected
            </span>
          )}
          <button
            onClick={() => setExpanded(!expanded)}
            className="text-gray-500 hover:text-gray-700 text-xs"
          >
            {expanded ? '▲ Less' : '▼ More'}
          </button>
        </div>
      </div>

      {/* Communication Text */}
      <div className="mb-3 p-3 bg-gray-50 rounded border border-gray-200">
        <p className="text-sm text-gray-900 whitespace-pre-wrap">{text}</p>
      </div>

      {/* Score Breakdown - Always Visible */}
      <div className="mb-3 pb-3 border-b border-gray-200">
        <ScoreBreakdown breakdown={communication.score_breakdown} />
      </div>

      {/* Expandable Details */}
      {expanded && (
        <div className="space-y-2 mb-3">
          <div className="p-2.5 rounded bg-green-50 border border-green-200">
            <div className="text-xs font-semibold text-green-900 mb-1">Why This Works</div>
            <p className="text-xs text-green-800 leading-relaxed">{communication.recommendation_reasoning}</p>
          </div>

          {communication.compliance_notes && (
            <div className="p-2.5 rounded bg-yellow-50 border border-yellow-200 flex gap-2">
              <span className="text-yellow-600 text-xs">⚠️</span>
              <div className="flex-1">
                <div className="text-xs font-semibold text-yellow-900 mb-0.5">Compliance Notes</div>
                <p className="text-xs text-yellow-800 leading-relaxed">{communication.compliance_notes}</p>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Action Buttons - Compact */}
      <div className="flex flex-wrap gap-1.5">
        <button
          onClick={handleCopy}
          className="px-2.5 py-1 text-xs bg-gray-100 hover:bg-gray-200 rounded transition-colors"
        >
          {copied ? '✓ Copied' : '📋 Copy'}
        </button>
        <button
          onClick={() => onEdit(communication)}
          className="px-2.5 py-1 text-xs bg-gray-100 hover:bg-gray-200 rounded transition-colors"
        >
          ✏️ Edit
        </button>
        <button
          onClick={handleSelect}
          className="px-2.5 py-1 text-xs bg-gray-100 hover:bg-gray-200 rounded transition-colors"
        >
          {selected ? '⭐ Selected' : '☆ Select'}
        </button>
        <div className="relative group">
          <button className="px-2.5 py-1 text-xs bg-gray-100 hover:bg-gray-200 rounded transition-colors">
            📥 Export
          </button>
          <div className="absolute left-0 mt-1 hidden group-hover:block bg-white border border-gray-300 rounded shadow-lg z-10 min-w-[120px]">
            <button
              onClick={() => exportCommunication(communication, 'txt', campaign)}
              className="block w-full text-left px-3 py-1.5 hover:bg-gray-100 text-xs"
            >
              Export as TXT
            </button>
            <button
              onClick={() => exportCommunication(communication, 'csv', campaign)}
              className="block w-full text-left px-3 py-1.5 hover:bg-gray-100 text-xs"
            >
              Export as CSV
            </button>
            <button
              onClick={() => exportCommunication(communication, 'json', campaign)}
              className="block w-full text-left px-3 py-1.5 hover:bg-gray-100 text-xs"
            >
              Export as JSON
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
