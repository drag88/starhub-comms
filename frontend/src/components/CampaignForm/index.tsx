import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { Sparkles, Layers, Target, Settings, Clock, ChevronRight } from 'lucide-react';
import type { CampaignFormData, Cohort, Product, Objective } from '@/types/campaign';
import { campaignAPI } from '@/services/api';
import { Input } from '@/components/shared/Input';
import { Select } from '@/components/shared/Select';
import { Button } from '@/components/shared/Button';
import { ChannelSelector } from './ChannelSelector';
import { CohortSelector } from './CohortSelector';
import { PromotionInput } from './PromotionInput';
import { CustomizationPanel } from './CustomizationPanel';

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
      product_lines: ['mobile_postpaid'],
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
    for (const cohort of cohorts) {
      const cohortLower = cohort.toLowerCase();
      if (cohortLower.includes('broadband') || cohortLower.includes('fiber') || cohortLower.includes('10gbps') || cohortLower.includes('premium_segment')) {
        return ['broadband_fiber', 'broadband_10gbps'];
      }
      if (cohortLower.includes('bundle') || cohortLower.includes('triple')) {
        return ['bundle_homehub'];
      }
      if (cohortLower.includes('entertainment') || cohortLower.includes('sports') || cohortLower.includes('streaming')) {
        return ['entertainment_tv'];
      }
    }
    return ['mobile_postpaid'];
  };

  const onSubmit = async (data: CampaignFormData) => {
    setLoading(true);
    setError(null);

    try {
      const inferredProductLines = inferProductLines(data.cohorts);
      const campaignData = {
        ...data,
        product_lines: inferredProductLines
      };

      console.log('Submitting campaign data:', JSON.stringify(campaignData, null, 2));

      const campaignResponse = await campaignAPI.create(campaignData);
      const campaignId = campaignResponse.data.campaign_id;

      await campaignAPI.generate(campaignId);

      if (generateCreatives && (campaignData.channel === 'email' || campaignData.channel === 'push')) {
        try {
          await campaignAPI.generateCreatives(campaignId);
        } catch (creativeError) {
          console.error('Creative generation failed:', creativeError);
        }
      }

      if (onGenerateComplete) {
        onGenerateComplete(campaignId);
      }
    } catch (err: any) {
      console.error('Generation error:', err);
      
      if (err.response?.status === 422 && err.response?.data?.errors) {
        const validationErrors = err.response.data.errors;
        const errorMessages = validationErrors.map((error: any) => {
          const field = error.loc?.slice(1).join('.') || 'field';
          const fieldName = field.replace(/_/g, ' ').replace(/\b\w/g, (l: string) => l.toUpperCase());
          return `• ${fieldName}: ${error.msg}`;
        });
        setError(errorMessages.join('\n'));
      } else if (err.response?.status === 500) {
        const errorDetail = err.response?.data?.detail || err.response?.data?.message || 'Server error occurred';
        setError(`Generation failed: ${errorDetail}`);
      } else if (!err.response) {
        setError('Generation failed: Connection error. Please ensure the backend is running.');
      } else {
        const errorDetail = err.response?.data?.detail || err.response?.data?.message || err.message || 'Failed to generate communications';
        setError(`Generation failed: ${errorDetail}`);
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-5xl mx-auto">
      <div className="flex items-center gap-3 mb-8">
        <div className="p-2 rounded-lg bg-primary/10 border border-primary/20">
          <Sparkles className="w-5 h-5 text-primary" />
        </div>
        <h2 className="text-2xl font-bold text-white tracking-tight">New Campaign Initialization</h2>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-8">
        {/* Campaign Information Section */}
        <section className="glass-panel rounded-xl overflow-hidden">
          <div className="px-6 py-4 border-b border-white/5 bg-white/[0.02] flex items-center gap-3">
            <Layers className="w-4 h-4 text-primary" />
            <h3 className="text-xs font-bold text-white uppercase tracking-widest">
              Section 01 // Campaign Details
            </h3>
          </div>
          <div className="p-6 space-y-6">
            <div className="grid grid-cols-1 gap-6">
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
          </div>
        </section>

        {/* Target Cohorts Section */}
        <section className="glass-panel rounded-xl overflow-hidden">
          <div className="px-6 py-4 border-b border-white/5 bg-white/[0.02] flex items-center gap-3">
            <Target className="w-4 h-4 text-primary" />
            <h3 className="text-xs font-bold text-white uppercase tracking-widest">
              Section 02 // Target Audience
            </h3>
          </div>
          <div className="p-6">
            <CohortSelector
              cohorts={cohorts}
              selectedCohorts={watch('cohorts') || []}
              onChange={(value) => setValue('cohorts', value)}
              error={errors.cohorts?.message}
            />
          </div>
        </section>

        {/* Promotion & Customization Section */}
        <section className="glass-panel rounded-xl overflow-hidden">
          <div className="px-6 py-4 border-b border-white/5 bg-white/[0.02] flex items-center gap-3">
            <Settings className="w-4 h-4 text-primary" />
            <h3 className="text-xs font-bold text-white uppercase tracking-widest">
              Section 03 // Configuration
            </h3>
          </div>
          <div className="p-6 space-y-8">
            <PromotionInput
              value={watch('promotion_details')}
              onChange={(value) => setValue('promotion_details', value)}
            />
            <div className="h-px bg-gradient-to-r from-transparent via-white/10 to-transparent" />
            <CustomizationPanel
              value={watch('customization')}
              onChange={(value) => setValue('customization', value)}
            />
          </div>
        </section>

        {/* Creative Generation Option */}
        {supportsCreatives && (
          <section className="glass-panel rounded-xl overflow-hidden p-1">
            <label 
              className={`
                relative flex items-start gap-4 p-6 rounded-lg cursor-pointer transition-all duration-300
                ${generateCreatives 
                  ? 'bg-primary/10 border border-primary/30 shadow-[0_0_20px_rgba(0,166,81,0.1)]' 
                  : 'hover:bg-white/5 border border-transparent'
                }
              `}
            >
              <div className="pt-1">
                <input
                  type="checkbox"
                  checked={generateCreatives}
                  onChange={(e) => setGenerateCreatives(e.target.checked)}
                  className="sr-only"
                />
                <div className={`w-5 h-5 rounded border flex items-center justify-center transition-colors ${generateCreatives ? 'bg-primary border-primary' : 'border-zinc-600 bg-zinc-900'}`}>
                  {generateCreatives && <Sparkles className="w-3 h-3 text-white" />}
                </div>
              </div>
              <div className="flex-1">
                <div className="flex items-center justify-between">
                  <span className={`text-base font-bold ${generateCreatives ? 'text-primary' : 'text-white'}`}>
                    Generate Creative Visuals
                  </span>
                  {generateCreatives && (
                    <span className="text-[10px] font-bold uppercase tracking-wider text-primary px-2 py-1 rounded bg-primary/10 border border-primary/20">
                      Active
                    </span>
                  )}
                </div>
                <p className="text-sm text-zinc-400 mt-1 max-w-2xl">
                  Enable AI image generation to create 3 optimized visual variants for your {selectedChannel} campaign.
                </p>
                <div className="mt-3 flex items-center gap-2 text-xs text-zinc-500">
                  <Clock className="w-3 h-3" />
                  <span>Processing time: +30-60s</span>
                </div>
              </div>
            </label>
          </section>
        )}

        {error && (
          <div className="bg-red-500/10 border border-red-500/20 text-red-200 px-6 py-4 rounded-lg backdrop-blur-sm">
            <div className="font-bold mb-1 flex items-center gap-2">
              <div className="w-2 h-2 rounded-full bg-red-500" />
              System Error
            </div>
            <div className="text-sm whitespace-pre-line pl-4 text-red-300/80">{error}</div>
          </div>
        )}

        <div className="pt-4 pb-12">
          <Button
            type="submit"
            variant="primary"
            loading={loading}
            className="w-full py-5 text-lg font-bold tracking-wide uppercase shadow-[0_0_30px_rgba(0,166,81,0.3)] hover:shadow-[0_0_50px_rgba(0,166,81,0.5)] border border-primary/50"
          >
            <div className="flex items-center justify-center gap-2">
              {loading ? 'Processing...' : 'Initiate Generation Sequence'}
              {!loading && <ChevronRight className="w-5 h-5" />}
            </div>
          </Button>
        </div>
      </form>
    </div>
  );
};

export default CampaignForm;
