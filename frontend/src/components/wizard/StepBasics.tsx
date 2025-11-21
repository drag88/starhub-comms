import { useConfig } from '@/contexts/ConfigContext';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import type { WizardStepProps } from './types';
import { WizardSection } from '@/components/wizard/WizardSection';

export function StepBasics({ data, updateData }: WizardStepProps) {
  const { objectives, cohorts } = useConfig();

  return (
    <div className="space-y-6">
      <WizardSection title="Campaign Information">
        <div className="space-y-2">
          <Label htmlFor="campaign_name">Campaign Name</Label>
          <Input
            id="campaign_name"
            placeholder="e.g., Summer 5G Promotion"
            value={data.campaign_name}
            onChange={(e) => updateData({ campaign_name: e.target.value })}
          />
          <p className="text-xs text-muted-foreground">
            Give your campaign a clear, descriptive name that reflects its purpose
          </p>
        </div>
      </WizardSection>

      <WizardSection title="Campaign Objective">
        <div className="space-y-2">
          <Label htmlFor="objective">Select Objective</Label>
          <Select
            value={data.objective}
            onValueChange={(value) => updateData({ objective: value })}
          >
            <SelectTrigger>
              <SelectValue placeholder="Select an objective" />
            </SelectTrigger>
            <SelectContent>
              {objectives.map((obj) => (
                <SelectItem key={obj.id} value={obj.id}>
                  {obj.name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          {data.objective && (
            <p className="text-sm text-muted-foreground">
              {objectives.find((o) => o.id === data.objective)?.description}
            </p>
          )}
        </div>
      </WizardSection>

      <WizardSection title="Target Audience">
        <div className="space-y-2">
          <Label htmlFor="cohort">Select Cohort</Label>
          <Select
            value={data.cohorts[0] || ''}
            onValueChange={(value) => updateData({ cohorts: [value] })}
          >
            <SelectTrigger>
              <SelectValue placeholder="Select a target cohort" />
            </SelectTrigger>
            <SelectContent>
              {cohorts.map((cohort) => (
                <SelectItem key={cohort.id} value={cohort.id}>
                  {cohort.name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          {data.cohorts[0] && (
            <p className="text-sm text-muted-foreground">
              {cohorts.find((c) => c.id === data.cohorts[0])?.description}
            </p>
          )}
        </div>
      </WizardSection>
    </div>
  );
}

