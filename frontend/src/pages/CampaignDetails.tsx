import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { format } from 'date-fns';
import { 
    RefreshCw, Download, ArrowLeft, MessageSquare, Image as ImageIcon,
    Users, ShoppingBag, Target
} from 'lucide-react';

import { Button } from '@/components/shared/Button';
import { CommunicationCard } from '@/components/results/CommunicationCard';
import { CreativeFeedbackModal } from '@/components/shared/CreativeFeedbackModal';
import { CreativeGallery } from '@/components/CreativeGallery';
import { campaignAPI, communicationAPI, creativeAPI } from '@/services/api';
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

  if (loading) return <div className="p-8 text-center text-white">Loading details...</div>;
  if (!campaign) return <div className="p-8 text-center text-white">Campaign not found</div>;

  return (
    <div className="space-y-8 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex items-center gap-4">
        <Button variant="ghost" onClick={() => navigate('/')} className="px-2">
            <ArrowLeft className="h-5 w-5" />
        </Button>
        <div>
            <h1 className="text-3xl font-bold tracking-tight text-white">{campaign.campaign_name}</h1>
            <div className="flex items-center gap-3 text-sm text-zinc-400 mt-1">
                <span>{format(new Date(campaign.created_at), 'MMM d, yyyy')}</span>
                <span className="w-1 h-1 rounded-full bg-zinc-600" />
                <span className="px-2 py-0.5 rounded-full bg-white/5 border border-white/10 text-xs uppercase tracking-wider">
                    {campaign.channel}
                </span>
            </div>
        </div>
        <div className="ml-auto flex gap-3">
            <Button variant="secondary" onClick={handleRegenerate} loading={generating}>
                <RefreshCw className="mr-2 h-4 w-4" />
                Regenerate Text
            </Button>
            <Button variant="secondary">
                <Download className="mr-2 h-4 w-4" /> Export Campaign
            </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Sidebar Info */}
        <div className="space-y-6">
            <div className="glass-panel rounded-xl overflow-hidden">
                <div className="px-5 py-3 border-b border-white/5 bg-white/[0.02]">
                    <h3 className="text-xs font-bold text-white uppercase tracking-widest">Campaign Context</h3>
                </div>
                <div className="p-5 space-y-6">
                    <div>
                        <div className="flex items-center gap-2 text-xs font-bold text-zinc-500 uppercase tracking-wider mb-2">
                            <Target className="h-4 w-4" /> Objective
                        </div>
                        <p className="text-sm text-zinc-200">{campaign.objective}</p>
                    </div>
                    <div className="h-px bg-white/5" />
                    <div>
                        <div className="flex items-center gap-2 text-xs font-bold text-zinc-500 uppercase tracking-wider mb-2">
                            <Users className="h-4 w-4" /> Audience
                        </div>
                        <div className="flex flex-wrap gap-2">
                            {campaign.cohorts.map((cohort, i) => (
                                <span key={i} className="text-xs bg-primary/10 text-primary px-2 py-1 rounded border border-primary/20">
                                    {cohort}
                                </span>
                            ))}
                        </div>
                    </div>
                    <div className="h-px bg-white/5" />
                    <div>
                        <div className="flex items-center gap-2 text-xs font-bold text-zinc-500 uppercase tracking-wider mb-2">
                            <ShoppingBag className="h-4 w-4" /> Product
                        </div>
                        <div className="flex flex-wrap gap-2">
                            {campaign.product_lines.map((line, i) => (
                                <span key={i} className="text-xs bg-white/5 text-zinc-300 px-2 py-1 rounded border border-white/10">
                                    {line}
                                </span>
                            ))}
                        </div>
                    </div>
                </div>
            </div>
            
            {campaign.promotion_details && (
                <div className="glass-panel rounded-xl overflow-hidden">
                    <div className="px-5 py-3 border-b border-white/5 bg-white/[0.02]">
                        <h3 className="text-xs font-bold text-white uppercase tracking-widest">Offer Details</h3>
                    </div>
                    <div className="p-5 space-y-3 text-sm">
                        {campaign.promotion_details.promotion_name && (
                            <div className="font-medium text-primary">{campaign.promotion_details.promotion_name}</div>
                        )}
                         {campaign.promotion_details.pricing?.discount && (
                            <div className="flex justify-between items-center p-3 rounded bg-white/5 border border-white/5">
                                <span className="text-zinc-400">Discount Applied</span>
                                <span className="text-white font-bold">{campaign.promotion_details.pricing.discount}%</span>
                            </div>
                        )}
                    </div>
                </div>
            )}
        </div>

        {/* Main Content */}
        <div className="lg:col-span-2 space-y-6">
            <div className="flex border-b border-white/10">
                <button 
                    className={`px-6 py-3 text-sm font-bold border-b-2 transition-all duration-200 flex items-center gap-2 ${activeTab === 'communications' ? 'border-primary text-primary' : 'border-transparent text-zinc-500 hover:text-zinc-300'}`}
                    onClick={() => setActiveTab('communications')}
                >
                    <MessageSquare className="h-4 w-4" /> Communications
                </button>
                {isCreativeSupported(campaign) && (
                    <button 
                        className={`px-6 py-3 text-sm font-bold border-b-2 transition-all duration-200 flex items-center gap-2 ${activeTab === 'creatives' ? 'border-primary text-primary' : 'border-transparent text-zinc-500 hover:text-zinc-300'}`}
                        onClick={() => setActiveTab('creatives')}
                    >
                        <ImageIcon className="h-4 w-4" /> Creatives
                    </button>
                )}
            </div>

            {activeTab === 'communications' && (
                <div className="space-y-4 animate-in fade-in slide-in-from-bottom-4 duration-300">
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
                 <div className="animate-in fade-in slide-in-from-bottom-4 duration-300">
                    <CreativeGallery 
                        creatives={creatives}
                        campaign={campaign}
                        loading={generatingCreatives}
                        onGenerate={handleGenerateCreatives}
                        onRefresh={creatives.length > 0 ? () => setShowFeedbackModal(true) : undefined}
                    />
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
