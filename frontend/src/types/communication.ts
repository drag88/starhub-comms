export interface ScoreBreakdown {
  channel_best_practices: number;
  cohort_alignment: number;
  objective_effectiveness: number;
  compliance_safety: number;
}

export interface Communication {
  communication_id: number;
  campaign_id: number;
  variation_number: number;
  communication_text: string;
  recommendation_score: number;
  score_breakdown: ScoreBreakdown;
  recommendation_reasoning: string;
  compliance_notes: string;
  is_selected: boolean;
  edited_text?: string;
  created_at: string;
}

export interface GenerationResponse {
  campaign_id: number;
  communications: Communication[];
  generated_at: string;
}
