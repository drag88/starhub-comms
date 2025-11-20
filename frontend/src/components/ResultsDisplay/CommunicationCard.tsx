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
    <div className={`card ${isTop ? 'border-2 border-primary-500 shadow-glow' : ''}`}>
      {/* Header */}
      <div className="flex justify-between items-center mb-3">
        <div className="flex items-center gap-2">
          <span className="text-sm font-semibold text-slate-400">
            Variation {communication.variation_number}
          </span>
          <RecommendationBadge score={communication.recommendation_score} isTop={isTop} />
        </div>
        <div className="flex items-center gap-2">
          {selected && (
            <span className="px-2 py-0.5 bg-primary-900/30 text-primary-400 text-xs rounded font-medium border border-primary-500/30">
              Selected
            </span>
          )}
          <button
            onClick={() => setExpanded(!expanded)}
            className="text-slate-500 hover:text-slate-300 text-xs transition-colors"
          >
            {expanded ? '▲ Less' : '▼ More'}
          </button>
        </div>
      </div>

      {/* Communication Text */}
      <div className="mb-3 p-3 bg-slate-800/50 rounded border border-slate-700/50">
        <p className="text-sm text-slate-100 whitespace-pre-wrap">{text}</p>
      </div>

      {/* Score Breakdown - Always Visible */}
      <div className="mb-3 pb-3 border-b border-slate-700/50">
        <ScoreBreakdown breakdown={communication.score_breakdown} />
      </div>

      {/* Expandable Details */}
      {expanded && (
        <div className="space-y-2 mb-3">
          <div className="p-2.5 rounded bg-primary-900/20 border border-primary-500/30">
            <div className="text-xs font-semibold text-primary-400 mb-1">Why This Works</div>
            <p className="text-xs text-primary-200 leading-relaxed">{communication.recommendation_reasoning}</p>
          </div>

          {communication.compliance_notes && (
            <div className="p-2.5 rounded bg-yellow-900/20 border border-yellow-500/30 flex gap-2">
              <span className="text-yellow-500 text-xs">⚠️</span>
              <div className="flex-1">
                <div className="text-xs font-semibold text-yellow-500 mb-0.5">Compliance Notes</div>
                <p className="text-xs text-yellow-200 leading-relaxed">{communication.compliance_notes}</p>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Action Buttons - Compact */}
      <div className="flex flex-wrap gap-1.5">
        <button
          onClick={handleCopy}
          className="px-2.5 py-1 text-xs bg-slate-800 hover:bg-slate-700 text-slate-300 rounded transition-colors border border-slate-700"
        >
          {copied ? '✓ Copied' : '📋 Copy'}
        </button>
        <button
          onClick={() => onEdit(communication)}
          className="px-2.5 py-1 text-xs bg-slate-800 hover:bg-slate-700 text-slate-300 rounded transition-colors border border-slate-700"
        >
          ✏️ Edit
        </button>
        <button
          onClick={handleSelect}
          className="px-2.5 py-1 text-xs bg-slate-800 hover:bg-slate-700 text-slate-300 rounded transition-colors border border-slate-700"
        >
          {selected ? '⭐ Selected' : '☆ Select'}
        </button>
        <div className="relative group">
          <button className="px-2.5 py-1 text-xs bg-slate-800 hover:bg-slate-700 text-slate-300 rounded transition-colors border border-slate-700">
            📥 Export
          </button>
          <div className="absolute left-0 mt-1 hidden group-hover:block bg-slate-800 border border-slate-700 rounded shadow-lg z-10 min-w-[120px]">
            <button
              onClick={() => exportCommunication(communication, 'txt', campaign)}
              className="block w-full text-left px-3 py-1.5 hover:bg-slate-700 text-slate-300 text-xs"
            >
              Export as TXT
            </button>
            <button
              onClick={() => exportCommunication(communication, 'csv', campaign)}
              className="block w-full text-left px-3 py-1.5 hover:bg-slate-700 text-slate-300 text-xs"
            >
              Export as CSV
            </button>
            <button
              onClick={() => exportCommunication(communication, 'json', campaign)}
              className="block w-full text-left px-3 py-1.5 hover:bg-slate-700 text-slate-300 text-xs"
            >
              Export as JSON
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
