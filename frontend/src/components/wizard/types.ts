import type { CampaignFormData } from '@/types/campaign';

export interface WizardStepProps {
  data: CampaignFormData;
  updateData: (updates: Partial<CampaignFormData>) => void;
}

