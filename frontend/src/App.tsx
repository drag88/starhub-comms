import { useState, useEffect } from 'react';
import CampaignForm from '/Users/asreenivas/Library/CloudStorage/OneDrive-StarHubLtd/02_Data_Analytics/Scripts/29. Customer Comms Generator/frontend/src/components/CampaignForm';
import ChatInterface from '/Users/asreenivas/Library/CloudStorage/OneDrive-StarHubLtd/02_Data_Analytics/Scripts/29. Customer Comms Generator/frontend/src/components/ResultsDisplay/ChatInterface';
import { LoadingSpinner } from '/Users/asreenivas/Library/CloudStorage/OneDrive-StarHubLtd/02_Data_Analytics/Scripts/29. Customer Comms Generator/frontend/src/components/shared/LoadingSpinner';
import { utilityAPI, campaignAPI, communicationAPI } from '/Users/asreenivas/Library/CloudStorage/OneDrive-StarHubLtd/02_Data_Analytics/Scripts/29. Customer Comms Generator/frontend/src/services/api';
import type { Cohort, Product, Objective, Campaign } from '/Users/asreenivas/Library/CloudStorage/OneDrive-StarHubLtd/02_Data_Analytics/Scripts/29. Customer Comms Generator/frontend/src/types/campaign';
import type { Communication } from '/Users/asreenivas/Library/CloudStorage/OneDrive-StarHubLtd/02_Data_Analytics/Scripts/29. Customer Comms Generator/frontend/src/types/communication';
import starhubLogo from '/Users/asreenivas/Library/CloudStorage/OneDrive-StarHubLtd/02_Data_Analytics/Scripts/29. Customer Comms Generator/frontend/src/assets/starhub-logo.png';

function App() {
  const [cohorts, setCohorts] = useState<Cohort[]>([]);
  const [products, setProducts] = useState<Product[]>([]);
  const [objectives, setObjectives] = useState<Objective[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [currentCampaign, setCurrentCampaign] = useState<Campaign | null>(null);
  const [communications, setCommunications] = useState<Communication[]>([]);
  const [generationLoading, setGenerationLoading] = useState(false);

  useEffect(() => {
    loadConfigurationData();
  }, []);

  const loadConfigurationData = async () => {
    try {
      const [cohortsRes, productsRes, objectivesRes] = await Promise.all([
        utilityAPI.getCohorts(),
        utilityAPI.getProducts(),
        utilityAPI.getObjectives(),
      ]);

      setCohorts(cohortsRes.data.cohorts);
      setProducts(productsRes.data.products);
      setObjectives(objectivesRes.data.objectives);
    } catch (error: any) {
      console.error('Failed to load configuration:', error);
      setError('Failed to load application data. Please ensure the backend is running.');
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateComplete = async (campaignId: number) => {
    setGenerationLoading(true);
    try {
      // Load campaign details
      const campaignRes = await campaignAPI.get(campaignId);
      setCurrentCampaign(campaignRes.data);

      // Load communications
      const commsRes = await communicationAPI.list(campaignId);
      setCommunications(commsRes.data);
    } catch (error) {
      console.error('Failed to load campaign results:', error);
    } finally {
      setGenerationLoading(false);
    }
  };

  const handleRefresh = async () => {
    if (!currentCampaign) return;

    setGenerationLoading(true);
    try {
      await campaignAPI.regenerate(currentCampaign.campaign_id, {});
      const commsRes = await communicationAPI.list(currentCampaign.campaign_id);
      setCommunications(commsRes.data);
    } catch (error) {
      console.error('Failed to regenerate:', error);
    } finally {
      setGenerationLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <LoadingSpinner size="lg" />
          <p className="mt-4 text-gray-600">Loading application...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center max-w-md">
          <div className="text-6xl mb-4">⚠️</div>
          <h2 className="text-xl font-bold text-gray-900 mb-2">Connection Error</h2>
          <p className="text-gray-600 mb-4">{error}</p>
          <button
            onClick={loadConfigurationData}
            className="btn-primary"
          >
            Retry Connection
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 py-2">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">
                StarHub Customer Communications Generator
              </h1>
            </div>
            <img 
              src={starhubLogo} 
              alt="StarHub Logo" 
              className="h-10 w-auto"
            />
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 pt-2 pb-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <div>
            <CampaignForm
              cohorts={cohorts}
              products={products}
              objectives={objectives}
              onGenerateComplete={handleGenerateComplete}
            />
          </div>

          <div>
            <ChatInterface
              communications={communications}
              campaign={currentCampaign || undefined}
              loading={generationLoading}
              onRefresh={handleRefresh}
            />
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;
