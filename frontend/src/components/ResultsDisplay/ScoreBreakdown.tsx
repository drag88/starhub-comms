import React from 'react';
import type { ScoreBreakdown as ScoreBreakdownType } from '/Users/asreenivas/Library/CloudStorage/OneDrive-StarHubLtd/02_Data_Analytics/Scripts/29. Customer Comms Generator/frontend/src/types/communication';

interface ScoreBreakdownProps {
  breakdown: ScoreBreakdownType;
}

const scorePillars = [
  { 
    key: 'channel_best_practices' as const, 
    label: 'Channel Best Practices', 
    icon: '📱',
    weight: 30 // 30% weight
  },
  { 
    key: 'cohort_alignment' as const, 
    label: 'Cohort Alignment', 
    icon: '👥',
    weight: 30 // 30% weight
  },
  { 
    key: 'objective_effectiveness' as const, 
    label: 'Objective Effectiveness', 
    icon: '🎯',
    weight: 25 // 25% weight
  },
  { 
    key: 'compliance_safety' as const, 
    label: 'Compliance & Safety', 
    icon: '🛡️',
    weight: 15 // 15% weight
  },
];

export const ScoreBreakdown: React.FC<ScoreBreakdownProps> = ({ breakdown }) => {
  return (
    <div>
      <h4 className="text-xs font-semibold text-gray-600 mb-2">Score Breakdown</h4>
      <div className="grid grid-cols-2 gap-2">
        {scorePillars.map((pillar) => {
          const score = breakdown[pillar.key];
          const normalizedScore = Math.min(Math.max(score || 0, 0), 100);
          return (
            <div key={pillar.key} className="space-y-1">
              <div className="flex justify-between items-center text-xs">
                <span className="flex items-center gap-1">
                  <span>{pillar.icon}</span>
                  <span className="truncate">{pillar.label}</span>
                </span>
                <span className="font-semibold text-green-700 ml-1">{normalizedScore}/100</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-1.5 overflow-hidden">
                <div
                  className="h-1.5 rounded-full transition-all duration-300"
                  style={{ 
                    width: `${normalizedScore}%`, 
                    minWidth: normalizedScore > 0 ? '2px' : '0',
                    backgroundColor: '#00A651'
                  }}
                />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
