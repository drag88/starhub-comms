import React, { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import type { CampaignFormData, Cohort, Product, Objective } from '/Users/asreenivas/Library/CloudStorage/OneDrive-StarHubLtd/02_Data_Analytics/Scripts/29. Customer Comms Generator/frontend/src/types/campaign';
import { campaignAPI } from '/Users/asreenivas/Library/CloudStorage/OneDrive-StarHubLtd/02_Data_Analytics/Scripts/29. Customer Comms Generator/frontend/src/services/api';
import { Input } from '/Users/asreenivas/Library/CloudStorage/OneDrive-StarHubLtd/02_Data_Analytics/Scripts/29. Customer Comms Generator/frontend/src/components/shared/Input';
import { Select } from '/Users/asreenivas/Library/CloudStorage/OneDrive-StarHubLtd/02_Data_Analytics/Scripts/29. Customer Comms Generator/frontend/src/components/shared/Select';
import { Button } from '/Users/asreenivas/Library/CloudStorage/OneDrive-StarHubLtd/02_Data_Analytics/Scripts/29. Customer Comms Generator/frontend/src/components/shared/Button';
import { ChannelSelector } from '/Users/asreenivas/Library/CloudStorage/OneDrive-StarHubLtd/02_Data_Analytics/Scripts/29. Customer Comms Generator/frontend/src/components/CampaignForm/ChannelSelector';
import { CohortSelector } from '/Users/asreenivas/Library/CloudStorage/OneDrive-StarHubLtd/02_Data_Analytics/Scripts/29. Customer Comms Generator/frontend/src/components/CampaignForm/CohortSelector';
import { PromotionInput } from '/Users/asreenivas/Library/CloudStorage/OneDrive-StarHubLtd/02_Data_Analytics/Scripts/29. Customer Comms Generator/frontend/src/components/CampaignForm/PromotionInput';
import { CustomizationPanel } from '/Users/asreenivas/Library/CloudStorage/OneDrive-StarHubLtd/02_Data_Analytics/Scripts/29. Customer Comms Generator/frontend/src/components/CampaignForm/CustomizationPanel';

interface CampaignFormProps {
  cohorts: Cohort[];
  products: Product[];
  objectives: Objective[];
  onGenerateComplete?: (campaignId: number) => void;
}

export const CampaignForm: React.FC<CampaignFormProps> = ({
  cohorts,
  products: _products,
  objectives,
  onGenerateComplete,
}) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [generateCreatives, setGenerateCreatives] = useState(false);

  const { register, handleSubmit, watch, setValue, formState: { errors } } = useForm<CampaignFormData>({
    defaultValues: {
      campaign_name: '',
      channel: '',
      objective: '',
      product_lines: ['mobile_postpaid'], // Default value since product_lines is required by backend but removed from UI
      cohorts: [],
      customization: {
        tone: 'professional',
        custom_instructions: '',
        required_phrases: [],
        prohibited_words: [],
        length_preference: 'optimal',
      },
    },
  });

  // Watch the channel field to show/hide creative generation option
  const selectedChannel = watch('channel');
  const supportsCreatives = selectedChannel === 'email' || selectedChannel === 'push';

  // Reset creative generation checkbox when channel changes to non-supported channel
  React.useEffect(() => {
    if (!supportsCreatives && generateCreatives) {
      setGenerateCreatives(false);
    }
  }, [supportsCreatives, generateCreatives]);

  // Infer product_lines from selected cohorts
  const inferProductLines = (cohorts: string[]): string[] => {
    // Check cohort selections and map to appropriate product lines
    for (const cohort of cohorts) {
      const cohortLower = cohort.toLowerCase();

      // Broadband-related cohorts
      if (cohortLower.includes('broadband') || cohortLower.includes('fiber') || cohortLower.includes('10gbps') || cohortLower.includes('premium_segment')) {
        return ['broadband_fiber', 'broadband_10gbps'];
      }

      // Bundle-related cohorts
      if (cohortLower.includes('bundle') || cohortLower.includes('triple')) {
        return ['bundle_homehub'];
      }

      // Entertainment-related cohorts
      if (cohortLower.includes('entertainment') || cohortLower.includes('sports') || cohortLower.includes('streaming')) {
        return ['entertainment_tv'];
      }
    }

    // Default to mobile postpaid if no specific match
    return ['mobile_postpaid'];
  };

  const onSubmit = async (data: CampaignFormData) => {
    setLoading(true);
    setError(null);

    try {
      // Infer product_lines from cohorts instead of using hardcoded default
      const inferredProductLines = inferProductLines(data.cohorts);
      const campaignData = {
        ...data,
        product_lines: inferredProductLines
      };

      // Log the data being sent for debugging
      console.log('Submitting campaign data:', JSON.stringify(campaignData, null, 2));
      console.log('Inferred product_lines:', inferredProductLines, 'from cohorts:', data.cohorts);

      // Create campaign
      const campaignResponse = await campaignAPI.create(campaignData);
      const campaignId = campaignResponse.data.campaign_id;

      // Generate communications
      await campaignAPI.generate(campaignId);

      // Generate creatives if requested and channel supports it
      if (generateCreatives && (campaignData.channel === 'email' || campaignData.channel === 'push')) {
        try {
          await campaignAPI.generateCreatives(campaignId);
        } catch (creativeError) {
          console.error('Creative generation failed:', creativeError);
          // Don't fail the whole process if creative generation fails
          // User can regenerate later
        }
      }

      if (onGenerateComplete) {
        onGenerateComplete(campaignId);
      }
    } catch (err: any) {
      console.error('Generation error:', err);
      console.error('Error response:', err.response?.data);
      console.error('Error status:', err.response?.status);
      
      // Handle validation errors (422)
      if (err.response?.status === 422 && err.response?.data?.errors) {
        const validationErrors = err.response.data.errors;
        const errorMessages = validationErrors.map((error: any) => {
          const field = error.loc?.slice(1).join('.') || 'field'; // Remove 'body' from location
          const fieldName = field.replace(/_/g, ' ').replace(/\b\w/g, (l: string) => l.toUpperCase());
          return `• ${fieldName}: ${error.msg}`;
        });
        setError(errorMessages.join('\n'));
      } 
      // Handle server errors (500)
      else if (err.response?.status === 500) {
        const errorDetail = err.response?.data?.detail || err.response?.data?.message || 'Server error occurred';
        setError(`Generation failed: ${errorDetail}`);
      }
      // Handle network/connection errors
      else if (!err.response) {
        setError('Generation failed: Connection error. Please ensure the backend is running.');
      }
      // Handle other errors
      else {
        const errorDetail = err.response?.data?.detail || err.response?.data?.message || err.message || 'Failed to generate communications';
        setError(`Generation failed: ${errorDetail}`);
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card">
      <h2 className="text-xl font-bold mb-6 text-slate-100">Create Campaign</h2>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
        {/* Campaign Information Section */}
        <section className="border border-slate-700/50 rounded-lg p-5 bg-slate-800/30">
          <h3 className="text-lg font-semibold text-slate-100 mb-4 pb-2 border-b border-slate-700/50">
            Campaign Information
          </h3>
          <div className="space-y-4">
            <Input
              label="Campaign Name"
              placeholder="e.g., Q4 Mobile Retention Campaign"
              {...register('campaign_name', { required: 'Campaign name is required' })}
              error={errors.campaign_name?.message}
            />

            <ChannelSelector
              value={watch('channel')}
              onChange={(value) => setValue('channel', value)}
              error={errors.channel?.message}
            />

            <Select
              label="Objective"
              options={objectives.map(obj => ({
                value: obj.id || obj.name,
                label: obj.name || obj.objective_name || obj.id,
              }))}
              {...register('objective', { required: 'Objective is required' })}
              error={errors.objective?.message}
            />
          </div>
        </section>

        {/* Target Cohorts Section */}
        <section className="border border-slate-700/50 rounded-lg p-5 bg-slate-800/30">
          <h3 className="text-lg font-semibold text-slate-100 mb-4 pb-2 border-b border-slate-700/50">
            Target Cohorts
          </h3>
          <CohortSelector
            cohorts={cohorts}
            selectedCohorts={watch('cohorts') || []}
            onChange={(value) => setValue('cohorts', value)}
            error={errors.cohorts?.message}
          />
        </section>

        {/* Promotion & Customization Section */}
        <section className="border border-slate-700/50 rounded-lg p-5 bg-slate-800/30">
          <h3 className="text-lg font-semibold text-slate-100 mb-4 pb-2 border-b border-slate-700/50">
            Promotion & Customization
          </h3>
          <div className="space-y-6">
            <PromotionInput
              value={watch('promotion_details')}
              onChange={(value) => setValue('promotion_details', value)}
            />
            <div className="pt-4 border-t border-slate-700/50">
              <CustomizationPanel
                value={watch('customization')}
                onChange={(value) => setValue('customization', value)}
              />
            </div>
          </div>
        </section>

        {/* Creative Generation Option - Only show for Email/Push channels */}
        {supportsCreatives && (
          <section className="border border-slate-700/50 rounded-lg p-5 bg-slate-800/30">
            <div className="flex items-start gap-3">
              <input
                type="checkbox"
                id="generateCreatives"
                checked={generateCreatives}
                onChange={(e) => setGenerateCreatives(e.target.checked)}
                className="mt-1 h-5 w-5 text-primary-500 border-slate-600 rounded focus:ring-primary-500 bg-slate-900"
              />
              <div className="flex-1">
                <label htmlFor="generateCreatives" className="flex items-center gap-2 cursor-pointer">
                  <span className="text-lg font-semibold text-slate-100">
                    🎨 Generate Creative Images
                  </span>
                </label>
                <p className="text-sm text-slate-400 mt-1">
                  Automatically generate AI-powered creative images for your {selectedChannel} campaign.
                  This will create 3 image variants optimized for your channel.
                </p>
                <div className="mt-2 text-xs text-slate-400 bg-slate-800/50 p-2 rounded border border-slate-700/50">
                  ⏱️ Note: This may add 30-60 seconds to generation time
                </div>
              </div>
            </div>
          </section>
        )}

        {error && (
          <div className="bg-red-900/20 border border-red-800/50 text-red-200 px-4 py-3 rounded">
            <div className="font-semibold mb-1">Validation error</div>
            <div className="text-sm whitespace-pre-line">{error}</div>
          </div>
        )}

        <div className="pt-6 border-t border-slate-700/50 mt-8">
          <Button
            type="submit"
            variant="primary"
            loading={loading}
            className="w-full py-4 text-xl font-bold shadow-lg shadow-primary-500/20"
          >
            Generate Communications
          </Button>
        </div>
      </form>
    </div>
  );
};

export default CampaignForm;
