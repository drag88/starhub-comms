import { useState } from 'react';
import { Copy, Check, Edit2, Star, ChevronDown, ChevronUp, AlertTriangle } from 'lucide-react';
import { Card, CardContent, CardFooter, CardHeader } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { RecommendationBadge } from './RecommendationBadge';
import { ScoreBreakdown } from './ScoreBreakdown';
import type { Communication } from '@/types/communication';
import { communicationAPI } from '@/services/api';

interface CommunicationCardProps {
  communication: Communication;
  isTop?: boolean;
  onEdit?: (communication: Communication) => void;
}

export function CommunicationCard({ communication, isTop, onEdit }: CommunicationCardProps) {
  const [copied, setCopied] = useState(false);
  const [selected, setSelected] = useState(communication.is_selected);
  const [expanded, setExpanded] = useState(false);

  const text = communication.edited_text || communication.communication_text;

  const handleCopy = () => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleSelect = async () => {
    try {
      await communicationAPI.update(communication.communication_id, {
        is_selected: !selected,
      });
      setSelected(!selected);
    } catch (error) {
      console.error('Failed to update selection:', error);
    }
  };

  return (
    <Card className={isTop ? "border-primary shadow-md" : ""}>
      <CardHeader className="pb-2 flex flex-row items-start justify-between space-y-0">
        <div className="flex items-center gap-2">
            <Badge variant="outline">Var {communication.variation_number}</Badge>
            <RecommendationBadge score={communication.recommendation_score} isTop={isTop} />
            {selected && <Badge>Selected</Badge>}
        </div>
        <div className="flex items-center gap-1">
            <Button variant="ghost" size="sm" className="h-8 text-xs" onClick={() => setExpanded(!expanded)}>
                {expanded ? <ChevronUp className="h-3 w-3 mr-1" /> : <ChevronDown className="h-3 w-3 mr-1" />}
                Details
            </Button>
        </div>
      </CardHeader>
      <CardContent className="pb-2">
        <div className="p-4 bg-muted/40 rounded-md border text-sm whitespace-pre-wrap font-medium">
            {text}
        </div>
        <div className="mt-4">
            <ScoreBreakdown breakdown={communication.score_breakdown} />
        </div>

        {expanded && (
            <div className="mt-4 space-y-3 animate-accordion-down">
                <div className="p-3 bg-primary/5 rounded-md border border-primary/20">
                    <h4 className="text-xs font-semibold text-primary mb-1">Why This Works</h4>
                    <p className="text-xs text-muted-foreground">{communication.recommendation_reasoning}</p>
                </div>
                {communication.compliance_notes && (
                     <div className="p-3 bg-yellow-500/10 rounded-md border border-yellow-500/20 flex gap-2">
                        <AlertTriangle className="h-4 w-4 text-yellow-600 flex-shrink-0" />
                        <div>
                            <h4 className="text-xs font-semibold text-yellow-700 mb-1">Compliance Notes</h4>
                            <p className="text-xs text-yellow-700/80">{communication.compliance_notes}</p>
                        </div>
                     </div>
                )}
            </div>
        )}
      </CardContent>
      <CardFooter className="pt-2 justify-end gap-2">
        <Button variant="outline" size="sm" onClick={handleCopy}>
            {copied ? <Check className="h-3 w-3 mr-2" /> : <Copy className="h-3 w-3 mr-2" />}
            {copied ? "Copied" : "Copy"}
        </Button>
        <Button variant="outline" size="sm" onClick={() => onEdit?.(communication)}>
            <Edit2 className="h-3 w-3 mr-2" /> Edit
        </Button>
        <Button variant={selected ? "default" : "outline"} size="sm" onClick={handleSelect}>
            <Star className={`h-3 w-3 mr-2 ${selected ? "fill-current" : ""}`} />
            {selected ? "Selected" : "Select"}
        </Button>
      </CardFooter>
    </Card>
  );
}
