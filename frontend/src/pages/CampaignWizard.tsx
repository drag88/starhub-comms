import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ChevronRight, ChevronLeft, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { StepBasics } from '@/components/wizard/StepBasics';
import { StepDetails } from '@/components/wizard/StepDetails';
import { StepReview } from '@/components/wizard/StepReview';
import { campaignAPI } from '@/services/api';
import type { CampaignFormData } from '@/types/campaign';
import { Separator } from '@/components/ui/separator';

const INITIAL_DATA: CampaignFormData = {
  campaign_name: '',
  channel: '',
  objective: '',
  product_lines: [],
  cohorts: [],
  customization: {
    tone: 'professional',
    required_phrases: [],
    prohibited_words: [],
    length_preference: 'optimal',
    custom_instructions: '',
  },
  promotion_details: {
    promotion_name: '',
    features: [],
    pricing: {}
  }
};

const STEPS = ['Basics', 'Details', 'Review'];

export function CampaignWizard() {
  const [currentStep, setCurrentStep] = useState(0);
  const [formData, setFormData] = useState<CampaignFormData>(INITIAL_DATA);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const navigate = useNavigate();

  const updateData = (updates: Partial<CampaignFormData>) => {
    setFormData(prev => ({ ...prev, ...updates }));
  };

  const handleNext = () => {
    if (currentStep < STEPS.length - 1) {
      setCurrentStep(prev => prev + 1);
    } else {
      handleSubmit();
    }
  };

  const handleBack = () => {
    if (currentStep > 0) {
      setCurrentStep(prev => prev - 1);
    }
  };

  const handleSubmit = async () => {
    setIsSubmitting(true);
    try {
      // Remove UI-only flag before sending to backend
      const { generate_creatives, ...campaignData } = formData;

      const response = await campaignAPI.create(campaignData);
      const campaignId = response.data.campaign_id;

      // Trigger generation immediately after creation
      await campaignAPI.generate(campaignId);

      // Generate creatives if requested and channel supports it
      if (generate_creatives && (formData.channel === 'email' || formData.channel === 'push')) {
        try {
          await campaignAPI.generateCreatives(campaignId);
        } catch (creativeError) {
          console.error('Creative generation failed:', creativeError);
          // Don't fail the whole process if creative generation fails
        }
      }

      navigate(`/campaigns/${campaignId}`);
    } catch (error) {
      console.error('Failed to create campaign:', error);
      // Show error toast here (TODO: Implement toast)
      alert('Failed to create campaign. Please check the console for details.'); // Temporary fallback
    } finally {
      setIsSubmitting(false);
    }
  };

  const isStepValid = () => {
    switch (currentStep) {
      case 0:
        return formData.campaign_name && formData.objective && formData.cohorts.length > 0;
      case 1:
        return formData.product_lines.length > 0 && formData.channel;
      default:
        return true;
    }
  };

  return (
    <div className="max-w-5xl mx-auto py-8 px-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold tracking-tight">New Campaign</h1>
        <p className="text-muted-foreground">
          Create a new marketing campaign in 3 simple steps.
        </p>
      </div>

      <div className="flex items-center justify-between mb-8 px-2">
        {STEPS.map((step, index) => (
          <div key={step} className="flex items-center">
            <div className={`flex items-center justify-center w-8 h-8 rounded-full border-2 ${
              index <= currentStep 
                ? 'border-primary bg-primary text-primary-foreground' 
                : 'border-muted text-muted-foreground'
            }`}>
              {index + 1}
            </div>
            <span className={`ml-2 text-sm font-medium ${
              index <= currentStep ? 'text-foreground' : 'text-muted-foreground'
            }`}>
              {step}
            </span>
            {index < STEPS.length - 1 && (
              <Separator className="w-12 mx-4 hidden sm:block" />
            )}
          </div>
        ))}
      </div>

      <Card className="w-full">
        <CardHeader>
          <CardTitle>{STEPS[currentStep]}</CardTitle>
          <CardDescription>
            {currentStep === 0 && "Let's start with the basics of your campaign."}
            {currentStep === 1 && "Define your product offer and channel."}
            {currentStep === 2 && "Review your settings before generating content."}
          </CardDescription>
        </CardHeader>
        <CardContent>
          {currentStep === 0 && (
            <StepBasics data={formData} updateData={updateData} />
          )}
          {currentStep === 1 && (
            <StepDetails data={formData} updateData={updateData} />
          )}
          {currentStep === 2 && (
            <StepReview data={formData} />
          )}
        </CardContent>
      </Card>

      <div className="flex justify-between mt-6">
        <Button 
          variant="outline" 
          onClick={handleBack} 
          disabled={currentStep === 0 || isSubmitting}
        >
          <ChevronLeft className="mr-2 h-4 w-4" /> Back
        </Button>
        <Button 
          onClick={handleNext} 
          disabled={!isStepValid() || isSubmitting}
          type="button"
        >
          {isSubmitting ? (
            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
          ) : (
            currentStep === STEPS.length - 1 ? 'Generate Campaign' : 'Next Step'
          )}
          {!isSubmitting && currentStep !== STEPS.length - 1 && (
            <ChevronRight className="ml-2 h-4 w-4" />
          )}
        </Button>
      </div>
    </div>
  );
}

