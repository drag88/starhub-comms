import type { Communication } from '/Users/asreenivas/Library/CloudStorage/OneDrive-StarHubLtd/02_Data_Analytics/Scripts/29. Customer Comms Generator/frontend/src/types/communication';
import type { Campaign } from '/Users/asreenivas/Library/CloudStorage/OneDrive-StarHubLtd/02_Data_Analytics/Scripts/29. Customer Comms Generator/frontend/src/types/campaign';

export const exportCommunication = (
  communication: Communication,
  format: 'txt' | 'csv' | 'json',
  campaign?: Campaign
) => {
  let content: string;
  let filename: string;
  let mimeType: string;

  const text = communication.edited_text || communication.communication_text;

  switch (format) {
    case 'txt':
      content = text;
      filename = `starhub_comm_${communication.campaign_id}_v${communication.variation_number}.txt`;
      mimeType = 'text/plain';
      break;

    case 'csv':
      content = `"Channel","Objective","Text","Score"\n`;
      content += `"${campaign?.channel || 'N/A'}","${campaign?.objective || 'N/A'}","${text.replace(/"/g, '""')}","${communication.recommendation_score}"`;
      filename = `starhub_comm_${communication.campaign_id}_v${communication.variation_number}.csv`;
      mimeType = 'text/csv';
      break;

    case 'json':
      content = JSON.stringify({
        communication: {
          variation_number: communication.variation_number,
          text: text,
          recommendation_score: communication.recommendation_score,
          score_breakdown: communication.score_breakdown,
          compliance_notes: communication.compliance_notes,
        },
        campaign: campaign ? {
          campaign_id: campaign.campaign_id,
          channel: campaign.channel,
          objective: campaign.objective,
          cohorts: campaign.cohorts,
        } : null,
        metadata: {
          generated_at: communication.created_at,
          exported_at: new Date().toISOString()
        }
      }, null, 2);
      filename = `starhub_comm_${communication.campaign_id}_v${communication.variation_number}.json`;
      mimeType = 'application/json';
      break;
  }

  // Trigger download
  const blob = new Blob([content], { type: mimeType });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
};
