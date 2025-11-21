import type { ReactNode } from 'react';
import { cn } from '@/lib/utils';

interface WizardSectionProps {
  title: string;
  description?: string;
  children: ReactNode;
  className?: string;
}

export function WizardSection({
  title,
  description,
  children,
  className,
}: WizardSectionProps) {
  return (
    <section
      className={cn(
        'w-full rounded-xl border border-white/5 bg-muted/20 p-4 space-y-4',
        className,
      )}
    >
      <div className="space-y-1">
        <h4 className="text-lg font-semibold">{title}</h4>
        {description && <p className="text-sm text-muted-foreground">{description}</p>}
      </div>
      {children}
    </section>
  );
}

