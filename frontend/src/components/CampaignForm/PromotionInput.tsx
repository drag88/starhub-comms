import React, { useState, useEffect } from 'react';
import { ChevronDown, Tag } from 'lucide-react';
import type { PromotionDetails } from '@/types/campaign';
import { Input } from '@/components/shared/Input';
import { Textarea } from '@/components/shared/Textarea';

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
    <div className="border border-white/5 rounded-lg overflow-hidden">
      <button
        type="button"
        onClick={() => setIsExpanded(!isExpanded)}
        className={`
          w-full flex items-center justify-between p-4 transition-all duration-200
          ${isExpanded ? 'bg-white/5 border-b border-white/5' : 'hover:bg-white/5 bg-transparent'}
        `}
      >
        <div className="flex items-center gap-3">
          <div className={`p-1.5 rounded ${isExpanded ? 'bg-primary/20 text-primary' : 'bg-zinc-800 text-zinc-400'}`}>
            <Tag className="w-4 h-4" />
          </div>
          <div className="text-left">
            <span className="text-sm font-bold text-zinc-200 block uppercase tracking-wide">Promotion Configuration</span>
            <span className="text-xs text-zinc-500">Optional details regarding pricing and offers</span>
          </div>
        </div>
        <ChevronDown
          className={`w-5 h-5 text-zinc-500 transition-transform duration-300 ${isExpanded ? 'rotate-180 text-primary' : ''}`}
        />
      </button>

      {isExpanded && (
        <div className="p-6 space-y-6 bg-black/20">
          <Input
            label="Promotion Name"
            placeholder="e.g., Unlimited Data Bundle Promo"
            value={value?.promotion_name || ''}
            onChange={(e) => updateField('promotion_name', e.target.value)}
          />

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
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

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
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

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
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
