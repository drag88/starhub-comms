import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { format } from 'date-fns';
import { 
    RefreshCw, Download, ArrowLeft, MessageSquare, Image as ImageIcon,
    Users, ShoppingBag
} from 'lucide-react';

import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';

import { CommunicationCard } from '@/components/results/CommunicationCard';
import { CreativeFeedbackModal } from '@/components/shared/CreativeFeedbackModal';
import { campaignAPI, communicationAPI, creativeAPI, API_BASE_URL } from '@/services/api';
import type { Campaign } from '@/types/campaign';
import type { Communication } from '@/types/communication';
import type { Creative } from '@/types/creative';

export function CampaignDetails() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [campaign, setCampaign] = useState<Campaign | null>(null);
  const [communications, setCommunications] = useState<Communication[]>([]);
  const [creatives, setCreatives] = useState<Creative[]>([]);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [generatingCreatives, setGeneratingCreatives] = useState(false);
  const [activeTab, setActiveTab] = useState("communications");
  const [showFeedbackModal, setShowFeedbackModal] = useState(false);

  const handleDownloadCreative = (imageUrl: string, filename: string) => {
      const fullUrl = `${API_BASE_URL}${imageUrl}`;
      const link = document.createElement('a');
      link.href = fullUrl;
      link.download = filename;
      link.target = '_blank';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
  };

  useEffect(() => {
    if (id) {
      loadCampaignData(parseInt(id));
    }
  }, [id]);

  const loadCampaignData = async (campaignId: number) => {
    try {
        setLoading(true);
        const [campRes, commsRes] = await Promise.all([
            campaignAPI.get(campaignId),
            communicationAPI.list(campaignId)
        ]);
        
        setCampaign(campRes.data);
        setCommunications(Array.isArray(commsRes.data) ? commsRes.data : []);
        
        // Try loading creatives if applicable
        try {
            if (isCreativeSupported(campRes.data)) {
                const creatRes = await creativeAPI.list(campaignId);
                if (creatRes?.data?.creatives) {
                    setCreatives(creatRes.data.creatives);
                }
            }
        } catch (e) {
            console.log("Creatives load error (optional)", e);
        }
        
    } catch (error) {
        console.error("Failed to load details:", error);
    } finally {
        setLoading(false);
    }
  };
  
  const isCreativeSupported = (c: Campaign) => {
      const channel = c.channel?.toLowerCase() || '';
      return channel.includes('email') || channel.includes('push');
  }

  const handleRegenerate = async () => {
      if (!campaign) return;
      setGenerating(true);
      try {
          await campaignAPI.regenerate(campaign.campaign_id, {});
          const commsRes = await communicationAPI.list(campaign.campaign_id);
          setCommunications(Array.isArray(commsRes.data) ? commsRes.data : []);
      } catch (e) {
          console.error("Regenerate failed", e);
      } finally {
          setGenerating(false);
      }
  };

  const handleGenerateCreatives = async () => {
      if (!campaign) return;

      // If creatives exist, show feedback modal for regeneration
      if (creatives.length > 0) {
          setShowFeedbackModal(true);
          return;
      }

      // First time generation - no feedback needed
      setGeneratingCreatives(true);
      try {
          await campaignAPI.generateCreatives(campaign.campaign_id);
          // Reload creatives
          const creatRes = await creativeAPI.list(campaign.campaign_id);
          if (creatRes?.data?.creatives) {
              setCreatives(creatRes.data.creatives);
          }
      } catch (e) {
          console.error("Creative generation failed", e);
          alert('Failed to generate creatives. Please try again.');
      } finally {
          setGeneratingCreatives(false);
      }
  };

  const handleRegenerateWithFeedback = async (feedback: string) => {
      if (!campaign) return;

      setGeneratingCreatives(true);
      setShowFeedbackModal(false);

      try {
          await creativeAPI.regenerate(campaign.campaign_id, feedback);
          // Reload creatives
          const creatRes = await creativeAPI.list(campaign.campaign_id);
          if (creatRes?.data?.creatives) {
              setCreatives(creatRes.data.creatives);
          }
      } catch (e) {
          console.error("Creative regeneration failed", e);
          alert('Failed to regenerate creatives. Please try again.');
      } finally {
          setGeneratingCreatives(false);
      }
  };

  if (loading) return <div className="p-8 text-center">Loading details...</div>;
  if (!campaign) return <div className="p-8 text-center">Campaign not found</div>;

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Button variant="ghost" size="icon" onClick={() => navigate('/')}>
            <ArrowLeft className="h-4 w-4" />
        </Button>
        <div>
            <h1 className="text-2xl font-bold tracking-tight">{campaign.campaign_name}</h1>
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <span>{format(new Date(campaign.created_at), 'MMM d, yyyy')}</span>
                <span>•</span>
                <Badge variant="outline" className="text-xs">{campaign.channel}</Badge>
            </div>
        </div>
        <div className="ml-auto flex gap-2">
            <Button variant="outline" onClick={handleRegenerate} disabled={generating}>
                <RefreshCw className={`mr-2 h-4 w-4 ${generating ? 'animate-spin' : ''}`} />
                Regenerate
            </Button>
            <Button variant="outline">
                <Download className="mr-2 h-4 w-4" /> Export
            </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Sidebar Info */}
        <div className="space-y-6">
            <Card>
                <CardHeader>
                    <CardTitle className="text-base">Campaign Context</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                    <div>
                        <div className="flex items-center gap-2 text-sm font-medium text-muted-foreground mb-1">
                            <TargetIcon className="h-4 w-4" /> Objective
                        </div>
                        <p className="text-sm">{campaign.objective}</p>
                    </div>
                    <Separator />
                    <div>
                        <div className="flex items-center gap-2 text-sm font-medium text-muted-foreground mb-1">
                            <Users className="h-4 w-4" /> Audience
                        </div>
                        <p className="text-sm">{campaign.cohorts.join(', ')}</p>
                    </div>
                     <Separator />
                    <div>
                        <div className="flex items-center gap-2 text-sm font-medium text-muted-foreground mb-1">
                            <ShoppingBag className="h-4 w-4" /> Product
                        </div>
                        <p className="text-sm">{campaign.product_lines.join(', ')}</p>
                    </div>
                </CardContent>
            </Card>
            
            {campaign.promotion_details && (
                <Card>
                    <CardHeader>
                        <CardTitle className="text-base">Offer Details</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-2 text-sm">
                        {campaign.promotion_details.promotion_name && (
                            <div className="font-medium">{campaign.promotion_details.promotion_name}</div>
                        )}
                         {campaign.promotion_details.pricing?.discount && (
                            <div className="flex justify-between">
                                <span className="text-muted-foreground">Discount</span>
                                <span>{campaign.promotion_details.pricing.discount}%</span>
                            </div>
                        )}
                    </CardContent>
                </Card>
            )}
        </div>

        {/* Main Content */}
        <div className="md:col-span-2 space-y-6">
            <div className="flex border-b">
                <button 
                    className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${activeTab === 'communications' ? 'border-primary text-primary' : 'border-transparent text-muted-foreground hover:text-foreground'}`}
                    onClick={() => setActiveTab('communications')}
                >
                    <div className="flex items-center gap-2">
                        <MessageSquare className="h-4 w-4" /> Communications
                    </div>
                </button>
                {isCreativeSupported(campaign) && (
                    <button 
                        className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${activeTab === 'creatives' ? 'border-primary text-primary' : 'border-transparent text-muted-foreground hover:text-foreground'}`}
                        onClick={() => setActiveTab('creatives')}
                    >
                         <div className="flex items-center gap-2">
                            <ImageIcon className="h-4 w-4" /> Creatives
                        </div>
                    </button>
                )}
            </div>

            {activeTab === 'communications' && (
                <div className="space-y-4">
                    {communications.map((comm, idx) => (
                        <CommunicationCard 
                            key={comm.communication_id} 
                            communication={comm} 
                            campaign={campaign}
                            isTop={idx === 0}
                        />
                    ))}
                </div>
            )}

            {activeTab === 'creatives' && (
                 <div className="space-y-4">
                    {/* Generate Creatives Button */}
                    <div className="flex justify-between items-center">
                        <div>
                            <h3 className="text-lg font-semibold">Campaign Creatives</h3>
                            <p className="text-sm text-muted-foreground">
                                AI-powered creative images optimized for {campaign.channel}
                            </p>
                        </div>
                        <Button
                            onClick={handleGenerateCreatives}
                            disabled={generatingCreatives}
                            variant={creatives.length > 0 ? "outline" : "default"}
                        >
                            <RefreshCw className={`mr-2 h-4 w-4 ${generatingCreatives ? 'animate-spin' : ''}`} />
                            {generatingCreatives
                                ? 'Generating...'
                                : creatives.length > 0
                                    ? 'Regenerate Creatives'
                                    : '🎨 Generate Creatives'}
                        </Button>
                    </div>

                    {/* Loading State */}
                    {generatingCreatives && (
                        <div className="py-8 text-center">
                            <RefreshCw className="h-8 w-8 animate-spin mx-auto mb-2 text-muted-foreground" />
                            <p className="text-muted-foreground">Generating creative images... (30-60 seconds)</p>
                        </div>
                    )}

                    {/* Creatives Grid */}
                    {!generatingCreatives && (
                        <div className="grid grid-cols-2 gap-4">
                            {creatives.length > 0 ? creatives.map(creative => (
                                <Card key={creative.creative_id} className="overflow-hidden">
                                     <div className="aspect-video bg-muted relative">
                                         <img
                                            src={creative.image_url ? `${API_BASE_URL}${creative.image_url}` : ''}
                                            alt="Generated Creative"
                                            className="object-cover w-full h-full"
                                            onError={(e) => {
                                                console.error('Failed to load image:', creative.image_url);
                                                e.currentTarget.style.display = 'none';
                                            }}
                                         />
                                         {!creative.image_url && (
                                             <div className="absolute inset-0 flex items-center justify-center text-muted-foreground text-xs">
                                                 Image Preview
                                             </div>
                                         )}
                                     </div>
                                     <CardContent className="p-3">
                                         <div className="flex justify-between items-center">
                                             <Badge variant="outline">Score: {creative.recommendation_score}</Badge>
                                             <Button
                                                 size="sm"
                                                 variant="ghost"
                                                 onClick={() => handleDownloadCreative(creative.image_url, creative.image_filename)}
                                             >
                                                 <Download className="h-4 w-4" />
                                             </Button>
                                         </div>
                                     </CardContent>
                                </Card>
                            )) : (
                                <div className="col-span-2 py-8 text-center text-muted-foreground">
                                    <div className="text-4xl mb-2">🎨</div>
                                    <p>No creatives generated yet</p>
                                    <p className="text-sm mt-1">Click the button above to generate</p>
                                </div>
                            )}
                        </div>
                    )}
                 </div>
            )}
        </div>
      </div>

      {/* Creative Feedback Modal */}
      <CreativeFeedbackModal
        isOpen={showFeedbackModal}
        onClose={() => setShowFeedbackModal(false)}
        onSubmit={handleRegenerateWithFeedback}
        isLoading={generatingCreatives}
      />
    </div>
  );
}

function TargetIcon(props: any) {
    return (
        <svg
      {...props}
      xmlns="http://www.w3.org/2000/svg"
      width="24"
      height="24"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <circle cx="12" cy="12" r="10" />
      <circle cx="12" cy="12" r="6" />
      <circle cx="12" cy="12" r="2" />
    </svg>
    )
}
