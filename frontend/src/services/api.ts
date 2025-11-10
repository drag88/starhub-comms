import axios from 'axios';
import type { CampaignFormData, Campaign, Cohort, Product, Objective } from '/Users/asreenivas/Library/CloudStorage/OneDrive-StarHubLtd/02_Data_Analytics/Scripts/29. Customer Comms Generator/frontend/src/types/campaign';
import type { GenerationResponse, Communication } from '/Users/asreenivas/Library/CloudStorage/OneDrive-StarHubLtd/02_Data_Analytics/Scripts/29. Customer Comms Generator/frontend/src/types/communication';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

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
};

export const communicationAPI = {
  list: (campaignId: number) =>
    apiClient.get<Communication[]>(`/api/v1/campaigns/${campaignId}/communications`),

  update: (id: number, data: { is_selected?: boolean; edited_text?: string }) =>
    apiClient.put<Communication>(`/api/v1/communications/${id}`, data),
};

export const utilityAPI = {
  getCohorts: () => apiClient.get<{ cohorts: Cohort[] }>('/api/v1/cohorts'),
  getProducts: () => apiClient.get<{ products: Product[] }>('/api/v1/products'),
  getObjectives: () => apiClient.get<{ objectives: Objective[] }>('/api/v1/objectives'),
  getHealth: () => apiClient.get('/api/v1/health'),
};
