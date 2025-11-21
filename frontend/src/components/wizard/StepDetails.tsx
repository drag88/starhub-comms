import { useConfig } from '@/contexts/ConfigContext';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import type { WizardStepProps } from './types';
import { WizardSection } from '@/components/wizard/WizardSection';

export function StepDetails({ data, updateData }: WizardStepProps) {
  const { products } = useConfig();
  
  const updatePromotion = (field: string, value: any) => {
    updateData({
      promotion_details: {
        ...data.promotion_details,
        promotion_name: data.promotion_details?.promotion_name || '', // Ensure name exists
        [field]: value,
      }
    });
  };

  return (
    <div className="space-y-6">
      <WizardSection title="Product Line">
        <div className="space-y-2">
          <Label htmlFor="product">Select Product</Label>
          <Select
            value={data.product_lines[0] || ''}
            onValueChange={(value) => updateData({ product_lines: [value] })}
          >
            <SelectTrigger>
              <SelectValue placeholder="Select a product" />
            </SelectTrigger>
            <SelectContent>
              {products.map((product) => (
                <SelectItem key={product.id} value={product.id}>
                  {product.name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </WizardSection>

      <WizardSection title="Communication Channel">
        <div className="space-y-2">
          <Label htmlFor="channel">Select Channel</Label>
          <Select
            value={data.channel}
            onValueChange={(value) => updateData({ channel: value })}
          >
            <SelectTrigger>
              <SelectValue placeholder="Select a channel" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="email">Email</SelectItem>
              <SelectItem value="sms">SMS</SelectItem>
              <SelectItem value="push">Push Notification</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </WizardSection>

      {(data.channel === 'email' || data.channel === 'push') && (
        <WizardSection title="Generate Creative Images">
          <div className="flex items-start gap-3">
            <input
              type="checkbox"
              id="generateCreatives"
              checked={data.generate_creatives || false}
              onChange={(e) => updateData({ generate_creatives: e.target.checked })}
              className="mt-1 h-5 w-5 rounded border-input"
            />
            <div className="flex-1 space-y-2">
              <label
                htmlFor="generateCreatives"
                className="flex items-center gap-2 cursor-pointer font-medium"
              >
                🎨 Generate Creative Images
              </label>
              <p className="text-sm text-muted-foreground">
                Automatically generate AI-powered creative images for your {data.channel} campaign.
                This will create 3 image variants optimized for your channel.
              </p>
              <div className="text-xs text-muted-foreground bg-background/50 p-2 rounded border">
                ⏱️ Note: This may add 30-60 seconds to generation time
              </div>
            </div>
          </div>
        </WizardSection>
      )}

      <WizardSection title="Promotion Offer">
        <div className="space-y-2">
          <Label>Offer Name</Label>
          <Input
            placeholder="e.g. Summer Special"
            value={data.promotion_details?.promotion_name || ''}
            onChange={(e) => updatePromotion('promotion_name', e.target.value)}
          />
        </div>

        <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
          <div className="space-y-2">
            <Label>Discount (%)</Label>
            <Input
              type="number"
              placeholder="20"
              value={data.promotion_details?.pricing?.discount || ''}
              onChange={(e) =>
                updateData({
                  promotion_details: {
                    ...data.promotion_details,
                    promotion_name: data.promotion_details?.promotion_name || '',
                    pricing: {
                      ...data.promotion_details?.pricing,
                      discount: Number(e.target.value),
                    },
                  },
                })
              }
            />
          </div>
          <div className="space-y-2">
            <Label>Contract Duration (Months)</Label>
            <Input
              type="number"
              placeholder="12"
              value={data.promotion_details?.pricing?.contract_duration || ''}
              onChange={(e) =>
                updateData({
                  promotion_details: {
                    ...data.promotion_details,
                    promotion_name: data.promotion_details?.promotion_name || '',
                    pricing: {
                      ...data.promotion_details?.pricing,
                      contract_duration: Number(e.target.value),
                    },
                  },
                })
              }
            />
          </div>
        </div>

        <div className="space-y-2">
          <Label>Key Features (comma separated)</Label>
          <Input
            placeholder="5G Speed, Free Disney+, No Admin Fee"
            value={data.promotion_details?.features?.join(', ') || ''}
            onChange={(e) =>
              updatePromotion(
                'features',
                e.target.value.split(',').map((s) => s.trim()),
              )
            }
          />
        </div>

        <div className="space-y-2">
          <Label>Terms & Conditions</Label>
          <Textarea
            placeholder="Valid for new signups only..."
            value={data.promotion_details?.terms_conditions || ''}
            onChange={(e) => updatePromotion('terms_conditions', e.target.value)}
          />
        </div>
      </WizardSection>
    </div>
  );
}

