import { useState, useEffect, useMemo } from 'react';
import CampaignForm from '/Users/asreenivas/Library/CloudStorage/OneDrive-StarHubLtd/02_Data_Analytics/Scripts/29. Customer Comms Generator/frontend/src/components/CampaignForm';
import { UnifiedResults } from '/Users/asreenivas/Library/CloudStorage/OneDrive-StarHubLtd/02_Data_Analytics/Scripts/29. Customer Comms Generator/frontend/src/components/ResultsDisplay/UnifiedResults';
import { LoadingSpinner } from '/Users/asreenivas/Library/CloudStorage/OneDrive-StarHubLtd/02_Data_Analytics/Scripts/29. Customer Comms Generator/frontend/src/components/shared/LoadingSpinner';
import { utilityAPI, campaignAPI, communicationAPI, creativeAPI } from '/Users/asreenivas/Library/CloudStorage/OneDrive-StarHubLtd/02_Data_Analytics/Scripts/29. Customer Comms Generator/frontend/src/services/api';
import type { Cohort, Product, Objective, Campaign } from '/Users/asreenivas/Library/CloudStorage/OneDrive-StarHubLtd/02_Data_Analytics/Scripts/29. Customer Comms Generator/frontend/src/types/campaign';
import type { Communication } from '/Users/asreenivas/Library/CloudStorage/OneDrive-StarHubLtd/02_Data_Analytics/Scripts/29. Customer Comms Generator/frontend/src/types/communication';
import type { Creative } from '/Users/asreenivas/Library/CloudStorage/OneDrive-StarHubLtd/02_Data_Analytics/Scripts/29. Customer Comms Generator/frontend/src/types/creative';
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
  const [generationError, setGenerationError] = useState<string | null>(null);
  const [creatives, setCreatives] = useState<Creative[]>([]);
  const [creativesLoading, setCreativesLoading] = useState(false);

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
    setGenerationError(null);
    try {
      // Load campaign details
      const campaignRes = await campaignAPI.get(campaignId);
      if (!campaignRes?.data) {
        throw new Error('Invalid campaign response');
      }
      setCurrentCampaign(campaignRes.data);

      // Load communications
      const commsRes = await communicationAPI.list(campaignId);
      // Ensure we have an array
      const communicationsList = Array.isArray(commsRes.data) ? commsRes.data : [];
      setCommunications(communicationsList);

      // Load creatives if they exist
      try {
        const creativesRes = await creativeAPI.list(campaignId);
        if (creativesRes?.data?.creatives && Array.isArray(creativesRes.data.creatives)) {
          setCreatives(creativesRes.data.creatives);
        } else {
          setCreatives([]);
        }
      } catch (err) {
        // No creatives yet, that's okay
        console.log('No creatives found yet:', err);
        setCreatives([]);
      }
    } catch (error: any) {
      console.error('Failed to load campaign results:', error);
      const errorMessage = error?.response?.data?.detail || error?.message || 'Failed to load campaign results. Please try again.';
      setGenerationError(errorMessage);
      // Don't clear the campaign if it was already set
      if (!currentCampaign) {
        setCurrentCampaign(null);
        setCommunications([]);
        setCreatives([]);
      }
    } finally {
      setGenerationLoading(false);
    }
  };

  const handleRefresh = async () => {
    if (!currentCampaign) return;

    setGenerationLoading(true);
    setGenerationError(null);
    try {
      await campaignAPI.regenerate(currentCampaign.campaign_id, {});
      const commsRes = await communicationAPI.list(currentCampaign.campaign_id);
      const communicationsList = Array.isArray(commsRes.data) ? commsRes.data : [];
      setCommunications(communicationsList);
    } catch (error: any) {
      console.error('Failed to regenerate:', error);
      const errorMessage = error?.response?.data?.detail || error?.message || 'Failed to regenerate communications. Please try again.';
      setGenerationError(errorMessage);
    } finally {
      setGenerationLoading(false);
    }
  };

  const handleGenerateCreatives = async () => {
    if (!currentCampaign) return;

    setCreativesLoading(true);

    // Set 5 minute timeout (creative generation can take 2-3 minutes for 3 variants)
    const timeoutId = setTimeout(() => {
      setCreativesLoading(false);
      alert('Creative generation is taking longer than expected. This can take 2-3 minutes. Please check the backend logs or try again.');
    }, 300000); // 5 minutes

    try {
      const response = await creativeAPI.generate(currentCampaign.campaign_id);
      clearTimeout(timeoutId);
      setCreatives(response.data.creatives);
    } catch (error: any) {
      clearTimeout(timeoutId);
      console.error('Creative generation failed:', error);

      // Better error messages
      let message = 'Failed to generate creatives. Please try again.';
      if (error.response?.status === 404) {
        message = 'Campaign not found. Please refresh the page.';
      } else if (error.response?.status === 500) {
        message = 'Server error. Please try again later.';
      } else if (error.code === 'ERR_NETWORK') {
        message = 'Network error. Please check your connection.';
      }

      alert(message);
    } finally {
      setCreativesLoading(false);
    }
  };

  const handleRefreshCreatives = async () => {
    if (!currentCampaign) return;

    try {
      const response = await creativeAPI.list(currentCampaign.campaign_id);
      setCreatives(response.data.creatives);
    } catch (error) {
      console.error('Failed to refresh creatives:', error);
    }
  };

  const handleSelectCreative = async (creativeId: number) => {
    try {
      // Find if this creative is already selected
      const creative = creatives.find(c => c.creative_id === creativeId);
      if (!creative) return;

      // Toggle selection
      await creativeAPI.select(creativeId, !creative.is_selected);
      
      // Refresh creatives list
      await handleRefreshCreatives();
    } catch (error) {
      console.error('Failed to select creative:', error);
      alert('Failed to update selection. Please try again.');
    }
  };

  // Check if creatives are supported for this campaign
  const supportsCreatives = (campaign: Campaign | null): boolean => {
    try {
      if (!campaign || !campaign.channel) {
        return false;
      }
      const channel = String(campaign.channel).toLowerCase();
      return channel === 'email' || channel === 'push' || channel.includes('email') || channel.includes('push');
    } catch (err) {
      console.error('Error checking creative support:', err);
      return false;
    }
  };

  // Memoize creative support check
  const canGenerateCreatives = useMemo(() => {
    if (!currentCampaign) return false;
    try {
      if (!currentCampaign.channel) {
        return false;
      }
      const channel = String(currentCampaign.channel).toLowerCase();
      return channel === 'email' || channel === 'push' || channel.includes('email') || channel.includes('push');
    } catch (err) {
      console.error('Error checking creative support:', err);
      return false;
    }
  }, [currentCampaign]);

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

          <div className="space-y-6">
            {generationError && (
              <div className="card bg-red-50 border border-red-200 text-red-700 p-4">
                <div className="font-semibold mb-1">Generation Error</div>
                <div className="text-sm">{generationError}</div>
                <button
                  onClick={() => setGenerationError(null)}
                  className="mt-2 text-sm underline"
                >
                  Dismiss
                </button>
              </div>
            )}
            <UnifiedResults
              communications={communications}
              creatives={creatives}
              campaign={currentCampaign || undefined}
              communicationsLoading={generationLoading}
              creativesLoading={creativesLoading}
              canGenerateCreatives={canGenerateCreatives}
              onRefreshCommunications={handleRefresh}
              onGenerateCreatives={canGenerateCreatives ? handleGenerateCreatives : undefined}
              onRefreshCreatives={canGenerateCreatives ? handleRefreshCreatives : undefined}
              onSelectCreative={handleSelectCreative}
            />
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;
