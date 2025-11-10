import React, { useState, useEffect } from 'react';
import type { CustomizationOptions } from '/Users/asreenivas/Library/CloudStorage/OneDrive-StarHubLtd/02_Data_Analytics/Scripts/29. Customer Comms Generator/frontend/src/types/campaign';
import { Select } from '/Users/asreenivas/Library/CloudStorage/OneDrive-StarHubLtd/02_Data_Analytics/Scripts/29. Customer Comms Generator/frontend/src/components/shared/Select';
import { Textarea } from '/Users/asreenivas/Library/CloudStorage/OneDrive-StarHubLtd/02_Data_Analytics/Scripts/29. Customer Comms Generator/frontend/src/components/shared/Textarea';

interface CustomizationPanelProps {
  value: CustomizationOptions;
  onChange: (value: CustomizationOptions) => void;
}

const toneOptions = [
  { value: 'friendly', label: 'Friendly' },
  { value: 'urgent', label: 'Urgent' },
  { value: 'premium', label: 'Premium' },
  { value: 'value-focused', label: 'Value-Focused' },
  { value: 'professional', label: 'Professional' },
];

const lengthOptions = [
  { value: 'shorter', label: 'Shorter' },
  { value: 'optimal', label: 'Optimal' },
  { value: 'longer', label: 'Longer' },
];

export const CustomizationPanel: React.FC<CustomizationPanelProps> = ({
  value,
  onChange,
}) => {
  const [requiredPhrasesText, setRequiredPhrasesText] = useState('');
  const [prohibitedWordsText, setProhibitedWordsText] = useState('');

  // Sync text fields with array values when value changes externally
  useEffect(() => {
    setRequiredPhrasesText(value.required_phrases.join(', '));
  }, [value.required_phrases]);

  useEffect(() => {
    setProhibitedWordsText(value.prohibited_words.join(', '));
  }, [value.prohibited_words]);

  const updateField = (field: keyof CustomizationOptions, val: any) => {
    onChange({
      ...value,
      [field]: val,
    });
  };

  const handleRequiredPhrasesChange = (text: string) => {
    setRequiredPhrasesText(text);
  };

  const handleRequiredPhrasesBlur = () => {
    const phrases = requiredPhrasesText.split(',').map(p => p.trim()).filter(Boolean);
    updateField('required_phrases', phrases);
  };

  const handleProhibitedWordsChange = (text: string) => {
    setProhibitedWordsText(text);
  };

  const handleProhibitedWordsBlur = () => {
    const words = prohibitedWordsText.split(',').map(w => w.trim()).filter(Boolean);
    updateField('prohibited_words', words);
  };

  return (
    <div className="space-y-4">

      <div className="grid grid-cols-2 gap-4">
        <Select
          label="Tone"
          options={toneOptions}
          value={value.tone}
          onChange={(e) => updateField('tone', e.target.value)}
        />

        <Select
          label="Length Preference"
          options={lengthOptions}
          value={value.length_preference}
          onChange={(e) => updateField('length_preference', e.target.value)}
        />
      </div>

      <Textarea
        label="Custom Instructions"
        placeholder="Any specific instructions for generating communications..."
        rows={3}
        value={value.custom_instructions || ''}
        onChange={(e) => updateField('custom_instructions', e.target.value)}
      />

      <Textarea
        label="Required Phrases (comma-separated)"
        placeholder="e.g., Limited time offer, StarHub exclusive"
        rows={2}
        value={requiredPhrasesText}
        onChange={(e) => handleRequiredPhrasesChange(e.target.value)}
        onBlur={handleRequiredPhrasesBlur}
      />

      <Textarea
        label="Prohibited Words (comma-separated)"
        placeholder="e.g., cheap, discount"
        rows={2}
        value={prohibitedWordsText}
        onChange={(e) => handleProhibitedWordsChange(e.target.value)}
        onBlur={handleProhibitedWordsBlur}
      />
    </div>
  );
};
