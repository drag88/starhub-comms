import { Badge } from "@/components/ui/badge";

export function RecommendationBadge({ score, isTop }: { score: number; isTop?: boolean }) {
  let variant: "default" | "secondary" | "outline" | "destructive" = "outline";
  
  if (score >= 90) {
    variant = "default"; // Primary green
  } else if (score >= 80) {
    variant = "secondary";
  } else if (score < 60) {
    variant = "destructive";
  }
  
  return (
    <Badge variant={variant} className={isTop ? "bg-primary text-primary-foreground" : ""}>
      {score} Score
    </Badge>
  );
}

