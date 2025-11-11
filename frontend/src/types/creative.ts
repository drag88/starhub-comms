export interface Creative {
  creative_id: number;
  campaign_id: number;
  variant_number: number;  // 1, 2, or 3
  channel_type: 'email_header' | 'push_header';
  image_filename: string;
  image_url: string;  // "/static/creatives/..."
  prompt_used: string;
  generation_params: {
    width: number;
    height: number;
    content_type: string;
  };
  model_used: string;
  recommendation_score: number;  // 0-100
  score_reasoning: string;
  is_selected: boolean;
  created_at: string;
}

export interface CreativeListResponse {
  campaign_id: number;
  creatives: Creative[];
  total: number;
}
