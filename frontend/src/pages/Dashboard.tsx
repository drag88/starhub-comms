import { useEffect, useState, useMemo, useRef } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { 
  Plus, 
  ArrowRight, 
  TrendingUp, 
  Users, 
  Target, 
  DollarSign, 
  Activity,
  Calendar,
} from 'lucide-react';
import { format } from 'date-fns';
import { campaignAPI } from '@/services/api';
import type { Campaign } from '@/types/campaign';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { cn } from '@/lib/utils';

// --- Mock Data ---
const ENGAGEMENT_DATA_FULL = [
  { month: 'Jan', engagement: 65, conversion: 40 },
  { month: 'Feb', engagement: 59, conversion: 30 },
  { month: 'Mar', engagement: 80, conversion: 55 },
  { month: 'Apr', engagement: 81, conversion: 60 },
  { month: 'May', engagement: 76, conversion: 45 },
  { month: 'Jun', engagement: 85, conversion: 70 },
  { month: 'Jul', engagement: 89, conversion: 75 },
  { month: 'Aug', engagement: 92, conversion: 78 },
  { month: 'Sep', engagement: 88, conversion: 72 },
];

const MOCK_CHANNEL_DATA = [
  { name: 'Email', value: 45, color: '#00A651' },
  { name: 'SMS', value: 32, color: '#3b82f6' },
  { name: 'Push', value: 28, color: '#8b5cf6' },
];

const COHORT_PERFORMANCE = [
  { name: 'High Value', score: 88, color: '#00A651' },
  { name: 'Churn Risk', score: 72, color: '#3b82f6' },
  { name: 'New Users', score: 65, color: '#f59e0b' },
  { name: 'Inactive', score: 45, color: '#ef4444' },
];

// --- CSS Animated Components ---

const AnimatedAreaChart = ({ data, timeRange }: { data: typeof ENGAGEMENT_DATA_FULL, timeRange: string }) => {
  const [mounted, setMounted] = useState(false);
  const [hoveredIndex, setHoveredIndex] = useState<number | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const [dimensions, setDimensions] = useState({ width: 0, height: 0 });
  
  useEffect(() => {
    setMounted(false);
    const timer = setTimeout(() => setMounted(true), 50);
    return () => clearTimeout(timer);
  }, [timeRange]);

  useEffect(() => {
    if (!containerRef.current) return;
    
    const resizeObserver = new ResizeObserver((entries) => {
      const { width, height } = entries[0].contentRect;
      requestAnimationFrame(() => {
        setDimensions({ width, height });
      });
    });

    resizeObserver.observe(containerRef.current);
    return () => resizeObserver.disconnect();
  }, []);

  // Filter data based on time range
  const displayData = useMemo(() => {
    if (timeRange === '3m') return data.slice(-3);
    if (timeRange === '6m') return data.slice(-6);
    return data;
  }, [data, timeRange]);

  const { width, height } = dimensions;
  const padding = 20; 
  const maxVal = 100;

  const getX = (index: number) => {
    if (displayData.length <= 1) return padding;
    return (index / (displayData.length - 1)) * (width - padding * 2) + padding;
  };
  
  const getY = (val: number) => {
    return height - (val / maxVal) * (height - padding * 2) - padding;
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (!containerRef.current) return;
    const rect = containerRef.current.getBoundingClientRect();
    const x = e.clientX - rect.left - padding;
    const chartWidth = width - padding * 2;
    
    if (chartWidth <= 0) return;
    
    const index = Math.round((x / chartWidth) * (displayData.length - 1));
    const clampedIndex = Math.max(0, Math.min(index, displayData.length - 1));
    setHoveredIndex(clampedIndex);
  };

  const handleMouseLeave = () => {
    setHoveredIndex(null);
  };

  const createPath = (key: 'engagement' | 'conversion') => {
    if (displayData.length === 0 || width === 0) return '';
    const points = displayData.map((d, i) => `${getX(i)},${getY(d[key])}`);
    return `M ${points.join(' L ')}`;
  };

  const createArea = (key: 'engagement' | 'conversion') => {
    if (displayData.length === 0 || width === 0) return '';
    const linePath = createPath(key);
    return `${linePath} L ${getX(displayData.length - 1)},${height} L ${getX(0)},${height} Z`;
  };

  const pathStyle = {
    transition: 'd 0.8s cubic-bezier(0.4, 0, 0.2, 1), opacity 0.5s ease',
    opacity: mounted ? 1 : 0,
  };

  const lineStyle = {
    transition: 'd 0.8s cubic-bezier(0.4, 0, 0.2, 1), stroke-dashoffset 1s ease',
    strokeDasharray: 3000,
    strokeDashoffset: mounted ? 0 : 3000,
  };

  return (
    <div 
      className="w-full h-full min-h-[280px] flex flex-col relative cursor-crosshair" 
      ref={containerRef}
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
    >
      <div className="absolute top-0 left-0 right-0 bottom-8">
        <div className="w-full h-full flex flex-col justify-between text-[10px] text-muted-foreground/30 font-mono pointer-events-none">
          {[100, 75, 50, 25, 0].map((val) => (
            <div key={val} className="flex items-center w-full">
              <span className="w-6 text-right pr-2">{val}%</span>
              <div className="h-px flex-1 bg-border/30 border-t border-dashed border-border/50" />
            </div>
          ))}
        </div>
      
        {width > 0 && height > 0 && (
          <svg width={width} height={height} className="absolute inset-0 w-full h-full overflow-visible pointer-events-none">
            {/* Conversion Layer */}
            <path 
              d={createArea('conversion')} 
              fill="#3b82f6" 
              fillOpacity="0.1" 
              stroke="none"
              style={pathStyle}
            />
            <path 
              d={createPath('conversion')} 
              fill="none" 
              stroke="#3b82f6" 
              strokeWidth="2"
              style={lineStyle}
            />

            {/* Engagement Layer */}
            <path 
              d={createArea('engagement')} 
              fill="#00A651" 
              fillOpacity="0.15" 
              stroke="none"
              style={{ ...pathStyle, transitionDelay: '0.1s' }}
            />
            <path 
              d={createPath('engagement')} 
              fill="none" 
              stroke="#00A651" 
              strokeWidth="3"
              style={{ ...lineStyle, transitionDelay: '0.1s' }}
            />
          
            {/* Hover Line */}
            {hoveredIndex !== null && (
              <line 
                x1={getX(hoveredIndex)} 
                y1={0} 
                x2={getX(hoveredIndex)} 
                y2={height} 
                stroke="currentColor" 
                strokeOpacity="0.2" 
                strokeDasharray="4 4"
              />
            )}

            {/* Data Points */}
            {displayData.map((d, i) => {
              const isHovered = hoveredIndex === i;
              return (
                <g key={i}>
                  {/* Engagement Point */}
                  <circle 
                    cx={getX(i)} 
                    cy={getY(d.engagement)} 
                    r={isHovered ? 6 : 4} 
                    fill="#00A651"
                    stroke="white"
                    strokeWidth={isHovered ? 2 : 0}
                    className="transition-all duration-300 ease-out"
                    style={{ 
                      transformOrigin: `${getX(i)}px ${getY(d.engagement)}px`,
                      transform: mounted ? 'scale(1)' : 'scale(0)',
                      transitionDelay: `${0.5 + (i * 0.05)}s`
                    }}
                  />
                  
                  {/* Conversion Point */}
                  <circle 
                    cx={getX(i)} 
                    cy={getY(d.conversion)} 
                    r={isHovered ? 6 : 4} 
                    fill="#3b82f6"
                    stroke="white"
                    strokeWidth={isHovered ? 2 : 0}
                    className="transition-all duration-300 ease-out"
                    style={{ 
                      transformOrigin: `${getX(i)}px ${getY(d.conversion)}px`,
                      transform: mounted ? 'scale(1)' : 'scale(0)',
                      transitionDelay: `${0.5 + (i * 0.05)}s`
                    }}
                  />
                </g>
              );
            })}
          </svg>
        )}

        {/* Tooltip */}
        {hoveredIndex !== null && (
           <div 
             className="absolute bg-zinc-900/90 border border-white/10 backdrop-blur-md rounded-lg p-3 shadow-xl z-10 pointer-events-none transition-all duration-75"
             style={{ 
               left: getX(hoveredIndex), 
               top: 0,
               transform: `translate(-50%, -110%)`
             }}
           >
             <div className="text-xs font-bold text-center mb-2 border-b border-white/10 pb-1">
               {displayData[hoveredIndex].month}
             </div>
             <div className="space-y-1 text-xs">
               <div className="flex items-center gap-2">
                 <div className="w-2 h-2 rounded-full bg-[#00A651]" />
                 <span className="text-muted-foreground">Engagement:</span>
                 <span className="font-bold">{displayData[hoveredIndex].engagement}%</span>
               </div>
               <div className="flex items-center gap-2">
                 <div className="w-2 h-2 rounded-full bg-[#3b82f6]" />
                 <span className="text-muted-foreground">Conversion:</span>
                 <span className="font-bold">{displayData[hoveredIndex].conversion}%</span>
               </div>
             </div>
           </div>
        )}
      </div>

      {/* X Axis Labels */}
      <div className="absolute bottom-0 left-0 right-0 flex justify-between text-[10px] text-muted-foreground font-medium uppercase tracking-wider px-[20px]">
        {displayData.map((d, i) => (
          <span 
            key={d.month}
            className={`transition-all duration-300 ${hoveredIndex === i ? 'text-primary font-bold scale-110' : ''}`}
            style={{ 
              opacity: mounted ? 1 : 0,
              transform: mounted ? 'translateY(0)' : 'translateY(10px)',
              transitionDelay: `${0.2 + (i * 0.05)}s`
            }}
          >
            {d.month}
          </span>
        ))}
      </div>
    </div>
  );
};

const AnimatedBarChart = ({ data }: { data: typeof MOCK_CHANNEL_DATA }) => {
  const [mounted, setMounted] = useState(false);
  
  useEffect(() => {
    setMounted(true);
  }, []);

  const maxValue = Math.max(...data.map(d => d.value)) * 1.2;
  
  return (
    <div className="w-full h-full min-h-[200px] flex items-end justify-around gap-4 px-4 pb-2">
      {data.map((d, index) => {
        const heightPercent = (d.value / maxValue) * 100;
        return (
          <div key={d.name} className="flex-1 flex flex-col items-center gap-3 group h-full justify-end">
             {/* Tooltip Value */}
            <div 
              className="text-xs font-bold mb-1 text-white transition-all duration-500"
              style={{ 
                opacity: mounted ? 1 : 0,
                transform: mounted ? 'translateY(0)' : 'translateY(10px)',
                transitionDelay: `${0.5 + (index * 0.1)}s`
              }}
            >
              {d.value}
            </div>
            
            {/* Bar Track */}
            <div className="w-full max-w-[40px] h-[140px] bg-zinc-800/50 rounded-t-lg relative overflow-hidden">
              {/* Bar Fill */}
              <div 
                className="absolute bottom-0 left-0 right-0 rounded-t-lg transition-all duration-1000 ease-out"
                style={{ 
                  height: mounted ? `${heightPercent}%` : '0%',
                  backgroundColor: d.color,
                  transitionDelay: `${index * 0.1}s`
                }}
              >
                 {/* Gradient Overlay */}
                 <div className="absolute inset-0 bg-gradient-to-t from-black/20 to-white/10" />
              </div>
            </div>
            
            {/* Label */}
            <div className="text-[10px] uppercase tracking-wider font-bold text-muted-foreground">{d.name}</div>
          </div>
        );
      })}
    </div>
  );
};

export function Dashboard() {
  const [campaigns, setCampaigns] = useState<Campaign[]>([]);
  const [loading, setLoading] = useState(true);
  const [timeRange, setTimeRange] = useState('6m');
  const navigate = useNavigate();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    loadCampaigns();
    setMounted(true);
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

  // Calculate channel stats
  const channelStats = campaigns.reduce((acc, campaign) => {
    const channel = campaign.channel || 'Unknown';
    acc[channel] = (acc[channel] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);

  const channelData = Object.keys(channelStats).length > 0 
    ? Object.entries(channelStats).map(([name, value]) => ({
        name,
        value,
        color: name.toLowerCase() === 'email' ? '#00A651' : 
               name.toLowerCase() === 'sms' ? '#3b82f6' : 
               '#8b5cf6'
      }))
    : MOCK_CHANNEL_DATA;

  const getChannelBadgeVariant = (channel: string) => {
    switch (channel?.toLowerCase()) {
      case 'email': return 'default';
      case 'sms': return 'secondary';
      case 'push': return 'outline';
      default: return 'secondary';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-[50vh]">
        <div className="flex flex-col items-center gap-4">
           <div className="h-8 w-8 rounded-full border-2 border-primary border-t-transparent animate-spin" />
           <div className="text-muted-foreground text-sm">Initializing dashboard...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      {/* Header Section */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Executive Dashboard</h1>
          <p className="text-muted-foreground mt-1">
            Real-time insights and performance metrics.
          </p>
        </div>
        <Link to="/campaigns/new">
          <Button className="shadow-lg shadow-primary/10 hover:shadow-primary/25 transition-all">
            <Plus className="mr-2 h-4 w-4" /> New Campaign
          </Button>
        </Link>
      </div>

      {/* Key Performance Indicators */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card className="border-l-4 border-l-primary bg-card/50 backdrop-blur-sm hover:bg-card/80 transition-colors">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Revenue</CardTitle>
            <DollarSign className="h-4 w-4 text-primary" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">$1.2M</div>
            <p className="text-xs text-green-500 flex items-center mt-1">
              <TrendingUp className="h-3 w-3 mr-1" />
              +12.5% from last month
            </p>
          </CardContent>
        </Card>
        
        <Card className="border-l-4 border-l-blue-500 bg-card/50 backdrop-blur-sm hover:bg-card/80 transition-colors">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Campaigns</CardTitle>
            <Activity className="h-4 w-4 text-blue-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{campaigns.length}</div>
            <p className="text-xs text-muted-foreground mt-1">
              Across {Object.keys(channelStats).length} channels
            </p>
          </CardContent>
        </Card>

        <Card className="border-l-4 border-l-purple-500 bg-card/50 backdrop-blur-sm hover:bg-card/80 transition-colors">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Reach</CardTitle>
            <Users className="h-4 w-4 text-purple-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">2.4M</div>
            <p className="text-xs text-green-500 flex items-center mt-1">
              <TrendingUp className="h-3 w-3 mr-1" />
              +8.2% new customers
            </p>
          </CardContent>
        </Card>

        <Card className="border-l-4 border-l-amber-500 bg-card/50 backdrop-blur-sm hover:bg-card/80 transition-colors">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Avg. Engagement</CardTitle>
            <Target className="h-4 w-4 text-amber-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">24.8%</div>
            <p className="text-xs text-muted-foreground mt-1">
              +2.4% above benchmark
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Main Analytics Section */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-7 items-stretch">
        
        {/* Engagement Chart */}
        <Card className="col-span-4 bg-card/50 backdrop-blur-sm flex flex-col h-full">
          <CardHeader className="flex flex-row items-center justify-between pb-8 shrink-0">
            <div className="space-y-1">
              <CardTitle>Performance Trends</CardTitle>
              <CardDescription>
                Engagement vs Conversion rates.
              </CardDescription>
            </div>
            <Select value={timeRange} onValueChange={setTimeRange}>
              <SelectTrigger className="w-[160px] h-9 text-xs font-medium bg-white/5 border-white/10 hover:bg-white/10 hover:border-primary/50 transition-all rounded-lg">
                <div className="flex items-center gap-2">
                  <Calendar className="w-3.5 h-3.5 text-muted-foreground" />
                  <SelectValue placeholder="Time Range" />
                </div>
              </SelectTrigger>
              <SelectContent align="end" className="bg-zinc-950 border-white/10">
                <SelectItem value="3m" className="text-xs cursor-pointer">Last 3 Months</SelectItem>
                <SelectItem value="6m" className="text-xs cursor-pointer">Last 6 Months</SelectItem>
                <SelectItem value="all" className="text-xs cursor-pointer">All Time</SelectItem>
              </SelectContent>
            </Select>
          </CardHeader>
          <CardContent className="pl-2 pb-6 flex-1 min-h-0">
             <AnimatedAreaChart data={ENGAGEMENT_DATA_FULL} timeRange={timeRange} />
          </CardContent>
        </Card>

        {/* Channel Distribution & Cohorts */}
        <Card className="col-span-3 bg-card/50 backdrop-blur-sm flex flex-col h-full">
          <CardHeader className="shrink-0">
            <CardTitle>Channel Mix</CardTitle>
            <CardDescription>
              Distribution of active campaigns by channel.
            </CardDescription>
          </CardHeader>
          <CardContent className="flex-1 flex flex-col gap-8 min-h-0">
            <div className="h-[200px] w-full shrink-0">
              <AnimatedBarChart data={channelData} />
            </div>
            
            <div className="space-y-4 overflow-auto">
              <h4 className="text-sm font-medium text-muted-foreground flex items-center gap-2">
                <Users className="w-4 h-4" />
                Top Performing Cohorts
              </h4>
              <div className="space-y-4">
                {COHORT_PERFORMANCE.map((cohort, index) => (
                  <div 
                    key={cohort.name} 
                    className="space-y-1 transition-all duration-500 ease-out"
                    style={{ 
                      opacity: mounted ? 1 : 0,
                      transform: mounted ? 'translateX(0)' : 'translateX(-10px)',
                      transitionDelay: `${0.5 + (index * 0.1)}s`
                    }}
                  >
                    <div className="flex items-center justify-between text-sm">
                      <span className="font-medium">{cohort.name}</span>
                      <span className="font-mono text-xs text-muted-foreground">{cohort.score}%</span>
                    </div>
                    <div className="h-2 w-full rounded-full bg-zinc-800/50 overflow-hidden">
                      <div 
                        className="h-full rounded-full transition-all duration-1000 ease-out"
                        style={{ 
                          width: mounted ? `${cohort.score}%` : '0%',
                          backgroundColor: cohort.color,
                          transitionDelay: `${0.8 + (index * 0.1)}s`
                        }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Recent Campaigns - Compact List */}
      <Card className="bg-card/50 backdrop-blur-sm">
        <CardHeader className="flex flex-row items-center justify-between">
          <div>
            <CardTitle>Recent Campaigns</CardTitle>
            <CardDescription>
              Latest activity from your marketing team.
            </CardDescription>
          </div>
          <Button variant="ghost" size="sm" className="text-xs text-muted-foreground hover:text-primary" onClick={() => navigate('/campaigns')}>
            View All <ArrowRight className="ml-1 h-3 w-3" />
          </Button>
        </CardHeader>
        <CardContent>
          {campaigns.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-12 text-center">
              <div className="h-12 w-12 rounded-full bg-zinc-800/50 flex items-center justify-center mb-4">
                <Activity className="h-6 w-6 text-muted-foreground" />
              </div>
              <h3 className="text-lg font-medium">No recent activity</h3>
              <p className="text-sm text-muted-foreground mt-1 mb-6 max-w-xs">
                Start your first campaign to see analytics and insights here.
              </p>
              <Link to="/campaigns/new">
                <Button variant="outline">Create Campaign</Button>
              </Link>
            </div>
          ) : (
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {campaigns.slice(0, 6).map((campaign, i) => (
                <div
                  key={campaign.campaign_id}
                  className="group relative overflow-hidden rounded-lg border bg-background/50 p-4 hover:shadow-md transition-all hover:border-primary/50 cursor-pointer hover:bg-background transition-all duration-500"
                  style={{
                     opacity: mounted ? 1 : 0,
                     transform: mounted ? 'translateY(0)' : 'translateY(20px)',
                     transitionDelay: `${i * 0.05}s`
                  }}
                  onClick={() => navigate(`/campaigns/${campaign.campaign_id}`)}
                >
                  <div className="flex items-center justify-between mb-3">
                    <Badge variant={getChannelBadgeVariant(campaign.channel) as any} className="text-[10px] h-5 px-2">
                      {campaign.channel}
                    </Badge>
                    <span className="text-xs text-muted-foreground flex items-center font-mono">
                      {format(new Date(campaign.created_at), 'MMM d')}
                    </span>
                  </div>
                  
                  <h3 className="font-semibold text-sm truncate pr-4 group-hover:text-primary transition-colors">
                    {campaign.campaign_name}
                  </h3>
                  
                  <div className="mt-4 flex items-center justify-between">
                    <div className="text-xs text-muted-foreground truncate max-w-[70%] bg-zinc-800/50 px-2 py-1 rounded">
                      {campaign.product_lines[0] && campaign.product_lines[0].replace('_', ' ')}
                    </div>
                    <div className="h-6 w-6 rounded-full bg-primary/10 flex items-center justify-center opacity-0 -translate-x-2 group-hover:opacity-100 group-hover:translate-x-0 transition-all duration-300">
                      <ArrowRight className="h-3 w-3 text-primary" />
                    </div>
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
