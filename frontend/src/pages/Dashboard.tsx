import { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Plus, ArrowRight, Calendar, Target, Mail } from 'lucide-react';
import { format } from 'date-fns';
import { campaignAPI } from '@/services/api';
import type { Campaign } from '@/types/campaign';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';

export function Dashboard() {
  const [campaigns, setCampaigns] = useState<Campaign[]>([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    loadCampaigns();
  }, []);

  const loadCampaigns = async () => {
    try {
      const response = await campaignAPI.list();
      setCampaigns(response.data);
    } catch (error) {
      console.error('Failed to load campaigns:', error);
    } finally {
      setLoading(false);
    }
  };

  const getChannelBadgeVariant = (channel: string) => {
    switch (channel?.toLowerCase()) {
      case 'email':
        return 'default';
      case 'sms':
        return 'secondary';
      case 'push':
        return 'outline';
      default:
        return 'secondary';
    }
  };

  if (loading) {
    return <div className="p-8 text-center">Loading campaigns...</div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
          <p className="text-muted-foreground">
            Manage your customer communication campaigns.
          </p>
        </div>
        <Link to="/campaigns/new">
          <Button>
            <Plus className="mr-2 h-4 w-4" /> New Campaign
          </Button>
        </Link>
      </div>

      <div className="grid gap-4 md:grid-cols-3 mb-8">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">
              Total Campaigns
            </CardTitle>
            <Target className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{campaigns.length}</div>
            <p className="text-xs text-muted-foreground">
              +20.1% from last month
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">
              Active Channels
            </CardTitle>
            <Mail className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">3</div>
            <p className="text-xs text-muted-foreground">
              Email, SMS, Push Notification
            </p>
          </CardContent>
        </Card>
        {/* Add more stats cards as needed */}
      </div>

      <Card className="col-span-3">
        <CardHeader>
          <CardTitle>Recent Campaigns</CardTitle>
          <CardDescription>
            You have {campaigns.length} total campaigns.
          </CardDescription>
        </CardHeader>
        <CardContent>
          {campaigns.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-12 text-center">
              <div className="rounded-full bg-muted p-4 mb-4">
                <Target className="h-8 w-8 text-muted-foreground" />
              </div>
              <h3 className="text-lg font-semibold">No campaigns yet</h3>
              <p className="text-sm text-muted-foreground max-w-sm mt-2 mb-6">
                Get started by creating your first marketing campaign using our AI-powered generator.
              </p>
              <Link to="/campaigns/new">
                <Button>
                  <Plus className="mr-2 h-4 w-4" /> Create Campaign
                </Button>
              </Link>
            </div>
          ) : (
            <div className="space-y-4">
              {campaigns.map((campaign) => (
                <div
                  key={campaign.campaign_id}
                  className="group flex items-center justify-between space-x-4 rounded-md border p-4 hover:bg-muted/50 transition-colors cursor-pointer"
                  onClick={() => navigate(`/campaigns/${campaign.campaign_id}`)}
                >
                  <div className="flex items-center space-x-4">
                    <div className="rounded-full bg-primary/10 p-2">
                      <Target className="h-4 w-4 text-primary" />
                    </div>
                    <div>
                      <p className="text-sm font-medium leading-none group-hover:text-primary transition-colors">
                        {campaign.campaign_name}
                      </p>
                      <div className="flex items-center mt-1 space-x-2 text-xs text-muted-foreground">
                        <span className="flex items-center">
                          <Calendar className="mr-1 h-3 w-3" />
                          {format(new Date(campaign.created_at), 'MMM d, yyyy')}
                        </span>
                        <span>•</span>
                        <span>{campaign.product_lines.join(', ')}</span>
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center space-x-4">
                    <Badge variant={getChannelBadgeVariant(campaign.channel) as any}>
                      {campaign.channel}
                    </Badge>
                    <ArrowRight className="h-4 w-4 text-muted-foreground group-hover:translate-x-1 transition-transform" />
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

