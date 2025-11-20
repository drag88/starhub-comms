export interface CustomizationOptions {
  tone: string;
  custom_instructions?: string;
  required_phrases: string[];
  prohibited_words: string[];
  length_preference: string;
}

export interface PromotionDetails {
  promotion_name: string;
  pricing?: {
    monthly_price?: number;
    contract_duration?: number;
    discount?: number;
    bonus?: string;
  };
  features?: string[];
  terms_conditions?: string;
  validity_start?: string;
  validity_end?: string;
}

export interface CampaignFormData {
  campaign_name: string;
  channel: string;
  objective: string;
  product_lines: string[];
  cohorts: string[];
  promotion_details?: PromotionDetails;
  customization: CustomizationOptions;
  generate_creatives?: boolean; // UI-only flag for creative generation
}

export interface Campaign extends CampaignFormData {
  campaign_id: number;
  created_at: string;
  updated_at: string;
}

export interface Cohort {
  id: string;
  name: string;
  description: string;
  category: string;
  cohort_name?: string; // Legacy field for backward compatibility
  characteristics?: string[];
  preferred_channels?: string[];
  engagement_level?: string;
}

export interface Product {
  id: string;
  name: string;
  category: string;
  description?: string;
  product_line?: string; // Legacy field for backward compatibility
  target_cohorts?: string[];
  typical_objectives?: string[];
}

export interface Objective {
  id: string;
  name: string;
  description: string;
  typical_channels: string[];
  objective_name?: string; // Legacy field for backward compatibility
  key_metrics?: string[]; // Optional field
}
