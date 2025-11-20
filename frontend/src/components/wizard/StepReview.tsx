import type { CampaignFormData } from '@/types/campaign';
import { Badge } from '@/components/ui/badge';

export function StepReview({ data }: { data: CampaignFormData }) {
  return (
    <div className="space-y-6">
      <div className="space-y-4 border rounded-md p-4 bg-muted/20 w-full max-w-3xl mx-auto">
        <h4 className="font-medium text-lg">Campaign Summary</h4>
        <div className="space-y-4">
          <div>
            <h4 className="text-sm font-medium text-muted-foreground">Campaign Name</h4>
            <p className="font-medium mt-1">{data.campaign_name}</p>
          </div>
          <div>
            <h4 className="text-sm font-medium text-muted-foreground">Objective</h4>
            <p className="mt-1">{data.objective}</p>
          </div>
          <div>
            <h4 className="text-sm font-medium text-muted-foreground">Channel</h4>
            <div className="mt-1">
              <Badge variant="outline">{data.channel}</Badge>
            </div>
          </div>
          <div>
            <h4 className="text-sm font-medium text-muted-foreground">Target Audience</h4>
            <p className="mt-1">{data.cohorts.join(', ')}</p>
          </div>
          <div>
            <h4 className="text-sm font-medium text-muted-foreground">Product Line</h4>
            <p className="mt-1">{data.product_lines.join(', ')}</p>
          </div>
        </div>
      </div>

      <div className="space-y-4 border rounded-md p-4 bg-muted/20 w-full max-w-3xl mx-auto">
        <h4 className="font-medium text-lg">Promotion Offer</h4>
        <div className="space-y-4">
          <div>
            <h4 className="text-sm font-medium text-muted-foreground">Offer Name</h4>
            <p className="mt-1">{data.promotion_details?.promotion_name || '-'}</p>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <h4 className="text-sm font-medium text-muted-foreground">Discount</h4>
              <p className="mt-1">{data.promotion_details?.pricing?.discount ? `${data.promotion_details.pricing.discount}%` : '-'}</p>
            </div>
            <div>
              <h4 className="text-sm font-medium text-muted-foreground">Contract Duration</h4>
              <p className="mt-1">{data.promotion_details?.pricing?.contract_duration ? `${data.promotion_details.pricing.contract_duration} Months` : '-'}</p>
            </div>
          </div>
          <div>
            <h4 className="text-sm font-medium text-muted-foreground">Key Features</h4>
            <div className="flex flex-wrap gap-2 mt-1">
              {data.promotion_details?.features?.map((f, i) => (
                <Badge key={i} variant="secondary">{f}</Badge>
              ))}
              {(!data.promotion_details?.features || data.promotion_details.features.length === 0) && <p className="text-muted-foreground">-</p>}
            </div>
          </div>
          {data.promotion_details?.terms_conditions && (
            <div>
              <h4 className="text-sm font-medium text-muted-foreground">Terms & Conditions</h4>
              <p className="mt-1 text-sm">{data.promotion_details.terms_conditions}</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

