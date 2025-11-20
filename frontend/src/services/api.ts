import axios from 'axios';
import type { CampaignFormData, Campaign, Cohort, Product, Objective } from '/Users/asreenivas/Library/CloudStorage/OneDrive-StarHubLtd/02_Data_Analytics/Scripts/29. Customer Comms Generator/frontend/src/types/campaign';
import type { GenerationResponse, Communication } from '/Users/asreenivas/Library/CloudStorage/OneDrive-StarHubLtd/02_Data_Analytics/Scripts/29. Customer Comms Generator/frontend/src/types/communication';
import type { Creative, CreativeListResponse } from '/Users/asreenivas/Library/CloudStorage/OneDrive-StarHubLtd/02_Data_Analytics/Scripts/29. Customer Comms Generator/frontend/src/types/creative';

export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Error handling interceptor
apiClient.interceptors.response.use(
  response => response,
  error => {
    console.error('API Error:', error);
    return Promise.reject(error);
  }
);

export const campaignAPI = {
  create: (data: CampaignFormData) =>
    apiClient.post<Campaign>('/api/v1/campaigns/', data),

  get: (id: number) =>
    apiClient.get<Campaign>(`/api/v1/campaigns/${id}`),

  update: (id: number, data: Partial<CampaignFormData>) =>
    apiClient.put<Campaign>(`/api/v1/campaigns/${id}`, data),

  delete: (id: number) =>
    apiClient.delete(`/api/v1/campaigns/${id}`),

  list: (params?: { skip?: number; limit?: number; channel?: string }) =>
    apiClient.get<Campaign[]>('/api/v1/campaigns', { params }),

  generate: (id: number) =>
    apiClient.post<GenerationResponse>(`/api/v1/campaigns/${id}/generate`),

  regenerate: (id: number, updatedParams: Partial<CampaignFormData>) =>
    apiClient.post<GenerationResponse>(`/api/v1/campaigns/${id}/regenerate`, updatedParams),

  generateCreatives: (id: number) =>
    apiClient.post<CreativeListResponse>(`/api/v1/campaigns/${id}/generate-creatives`),
};

export const communicationAPI = {
  list: (campaignId: number) =>
    apiClient.get<Communication[]>(`/api/v1/campaigns/${campaignId}/communications`),

  update: (id: number, data: { is_selected?: boolean; edited_text?: string }) =>
    apiClient.put<Communication>(`/api/v1/communications/${id}`, data),
};

export const creativeAPI = {
  generate: (campaignId: number) =>
    apiClient.post<CreativeListResponse>(
      `/api/v1/campaigns/${campaignId}/generate-creatives`
    ),

  regenerate: (campaignId: number, feedback?: string) =>
    apiClient.post<CreativeListResponse>(
      `/api/v1/campaigns/${campaignId}/regenerate-creatives`,
      { feedback }
    ),

  list: (campaignId: number) =>
    apiClient.get<CreativeListResponse>(
      `/api/v1/campaigns/${campaignId}/creatives`
    ),

  get: (creativeId: number) =>
    apiClient.get<Creative>(`/api/v1/creatives/${creativeId}`),

  select: (creativeId: number, isSelected: boolean) =>
    apiClient.put<Creative>(
      `/api/v1/creatives/${creativeId}/select`,
      { is_selected: isSelected }
    ),

  delete: (creativeId: number) =>
    apiClient.delete(`/api/v1/creatives/${creativeId}`),
};

export const utilityAPI = {
  getCohorts: () => apiClient.get<{ cohorts: Cohort[] }>('/api/v1/cohorts'),
  getProducts: () => apiClient.get<{ products: Product[] }>('/api/v1/products'),
  getObjectives: () => apiClient.get<{ objectives: Objective[] }>('/api/v1/objectives'),
  getHealth: () => apiClient.get('/api/v1/health'),
};
