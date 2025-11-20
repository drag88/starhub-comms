import React, { useState } from 'react';
import { X, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';

interface CreativeFeedbackModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (feedback: string) => Promise<void>;
  isLoading?: boolean;
}

export const CreativeFeedbackModal: React.FC<CreativeFeedbackModalProps> = ({
  isOpen,
  onClose,
  onSubmit,
  isLoading = false,
}) => {
  const [feedback, setFeedback] = useState('');

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await onSubmit(feedback);
    setFeedback(''); // Reset after submit
  };

  const handleClose = () => {
    if (!isLoading) {
      setFeedback('');
      onClose();
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm">
      <div className="bg-card border border-border rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-border">
          <div>
            <h2 className="text-xl font-bold tracking-tight">Regenerate Creatives</h2>
            <p className="text-sm text-muted-foreground mt-1">
              Provide feedback to guide the regeneration of creative images
            </p>
          </div>
          <button
            onClick={handleClose}
            disabled={isLoading}
            className="text-muted-foreground hover:text-foreground disabled:opacity-50"
            aria-label="Close modal"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Content */}
        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          <div className="space-y-2">
            <Label htmlFor="feedback">
              Feedback (Optional)
            </Label>
            <Textarea
              id="feedback"
              value={feedback}
              onChange={(e) => setFeedback(e.target.value)}
              placeholder="E.g., Make the images more vibrant, include more dynamic poses, use brighter colors..."
              rows={6}
              className="resize-none"
              disabled={isLoading}
            />
            <p className="text-xs text-muted-foreground">
              Describe what you'd like to see improved in the new creative images.
              Leave blank to regenerate without specific feedback.
            </p>
          </div>

          {/* Examples */}
          <div className="border border-border rounded-md p-4 bg-muted/20">
            <h4 className="text-sm font-medium mb-2">Example Feedback:</h4>
            <ul className="text-xs text-muted-foreground space-y-1">
              <li>• "Use more vibrant colors with a modern aesthetic"</li>
              <li>• "Show people actively using the product"</li>
              <li>• "Make it look more premium and sophisticated"</li>
              <li>• "Include Singapore landmarks in the background"</li>
            </ul>
          </div>

          {/* Actions */}
          <div className="flex gap-3 justify-end pt-4 border-t border-border">
            <Button
              type="button"
              variant="outline"
              onClick={handleClose}
              disabled={isLoading}
            >
              Cancel
            </Button>
            <Button
              type="submit"
              disabled={isLoading}
              className="min-w-[140px]"
            >
              {isLoading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Generating...
                </>
              ) : (
                '🎨 Regenerate'
              )}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
};
