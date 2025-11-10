import React, { useState, useEffect } from 'react';
import type { PromotionDetails } from '/Users/asreenivas/Library/CloudStorage/OneDrive-StarHubLtd/02_Data_Analytics/Scripts/29. Customer Comms Generator/frontend/src/types/campaign';
import { Input } from '/Users/asreenivas/Library/CloudStorage/OneDrive-StarHubLtd/02_Data_Analytics/Scripts/29. Customer Comms Generator/frontend/src/components/shared/Input';
import { Textarea } from '/Users/asreenivas/Library/CloudStorage/OneDrive-StarHubLtd/02_Data_Analytics/Scripts/29. Customer Comms Generator/frontend/src/components/shared/Textarea';

interface PromotionInputProps {
  value?: PromotionDetails;
  onChange: (value: PromotionDetails | undefined) => void;
}

export const PromotionInput: React.FC<PromotionInputProps> = ({
  value,
  onChange,
}) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [featuresText, setFeaturesText] = useState('');

  const updateField = (field: keyof PromotionDetails, val: any) => {
    onChange({
      ...value,
      promotion_name: value?.promotion_name || '',
      [field]: val,
    } as PromotionDetails);
  };

  const updatePricing = (field: string, val: any) => {
    onChange({
      ...value,
      promotion_name: value?.promotion_name || '',
      pricing: {
        ...value?.pricing,
        [field]: val,
      },
    } as PromotionDetails);
  };

  // Sync featuresText with value.features when value changes externally
  useEffect(() => {
    if (value?.features) {
      setFeaturesText(value.features.join(', '));
    } else {
      setFeaturesText('');
    }
  }, [value?.features]);

  const handleFeaturesChange = (text: string) => {
    setFeaturesText(text);
  };

  const handleFeaturesBlur = () => {
    const features = featuresText.split(',').map(f => f.trim()).filter(Boolean);
    updateField('features', features);
  };

  return (
    <div>
      <button
        type="button"
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full flex items-center justify-between p-3 mb-3 bg-gray-50 hover:bg-gray-100 rounded-lg border border-gray-200 transition-colors"
      >
        <div className="flex items-center gap-2">
          <span className="text-sm font-medium text-gray-700">Promotion Details</span>
          <span className="text-xs text-gray-500">(Optional)</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-sm text-gray-600">{isExpanded ? 'Hide' : 'Show'}</span>
          <svg
            className={`w-4 h-4 text-gray-600 transition-transform ${isExpanded ? 'rotate-180' : ''}`}
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </div>
      </button>

      {isExpanded && (
        <div className="space-y-4">
          <Input
            label="Promotion Name"
            placeholder="e.g., Unlimited Data Bundle Promo"
            value={value?.promotion_name || ''}
            onChange={(e) => updateField('promotion_name', e.target.value)}
          />

          <div className="grid grid-cols-2 gap-4">
            <Input
              label="Monthly Price"
              type="number"
              placeholder="49.99"
              value={value?.pricing?.monthly_price || ''}
              onChange={(e) => updatePricing('monthly_price', parseFloat(e.target.value))}
            />

            <Input
              label="Contract Duration (months)"
              type="number"
              placeholder="24"
              value={value?.pricing?.contract_duration || ''}
              onChange={(e) => updatePricing('contract_duration', parseInt(e.target.value))}
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <Input
              label="Discount (%)"
              type="number"
              placeholder="20"
              value={value?.pricing?.discount || ''}
              onChange={(e) => updatePricing('discount', parseFloat(e.target.value))}
            />

            <Input
              label="Bonus Offer"
              placeholder="Free router"
              value={value?.pricing?.bonus || ''}
              onChange={(e) => updatePricing('bonus', e.target.value)}
            />
          </div>

          <Textarea
            label="Features (comma-separated)"
            placeholder="Unlimited data, 5G speeds, Free streaming"
            rows={3}
            value={featuresText}
            onChange={(e) => handleFeaturesChange(e.target.value)}
            onBlur={handleFeaturesBlur}
          />

          <Textarea
            label="Terms & Conditions"
            placeholder="Enter terms and conditions..."
            rows={3}
            value={value?.terms_conditions || ''}
            onChange={(e) => updateField('terms_conditions', e.target.value)}
          />

          <div className="grid grid-cols-2 gap-4">
            <Input
              label="Validity Start"
              type="date"
              value={value?.validity_start || ''}
              onChange={(e) => updateField('validity_start', e.target.value)}
            />

            <Input
              label="Validity End"
              type="date"
              value={value?.validity_end || ''}
              onChange={(e) => updateField('validity_end', e.target.value)}
            />
          </div>
        </div>
      )}
    </div>
  );
};
