import { cn } from "@/lib/utils";
import type { ScoreBreakdown as ScoreBreakdownType } from "@/types/communication";

interface BreakdownProps {
  breakdown?: ScoreBreakdownType;
}

export function ScoreBreakdown({ breakdown }: BreakdownProps) {
  if (!breakdown) return null;

  return (
    <div className="flex gap-4 text-xs">
      {Object.entries(breakdown).map(([key, value]) => (
        <div key={key} className="flex items-center gap-1.5">
          <span className="text-muted-foreground capitalize">{key.replace(/_/g, ' ')}</span>
          <div className="h-1.5 w-12 rounded-full bg-muted overflow-hidden">
             <div 
               className={cn(
                 "h-full rounded-full",
                 value >= 8 ? "bg-primary" : value >= 6 ? "bg-yellow-500" : "bg-red-500"
               )}
               style={{ width: `${value * 10}%` }}
             />
          </div>
          <span className="font-medium">{value}/10</span>
        </div>
      ))}
    </div>
  );
}
