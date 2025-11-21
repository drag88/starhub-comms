import React from 'react';

interface TextareaProps extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {
  label?: string;
  error?: string;
  showCharCount?: boolean;
  maxLength?: number;
}

export const Textarea: React.FC<TextareaProps> = ({
  label,
  error,
  showCharCount = false,
  maxLength,
  className = '',
  value,
  ...props
}) => {
  const charCount = typeof value === 'string' ? value.length : 0;

  return (
    <div className="w-full space-y-1.5">
      {label && (
        <label className="text-[10px] font-bold text-zinc-400 uppercase tracking-wider block ml-1">
          {label}
        </label>
      )}
      <div className="relative group">
        <div className="absolute -inset-0.5 bg-gradient-to-r from-primary/20 to-blue-500/20 rounded-lg blur opacity-0 group-focus-within:opacity-100 transition duration-500" />
        <textarea
          className={`
            relative w-full bg-zinc-900/80 border rounded-lg px-4 py-3 text-sm text-zinc-200 placeholder:text-zinc-600
            transition-all duration-200 min-h-[100px] resize-y
            focus:outline-none focus:ring-1 focus:ring-primary/50
            ${error 
              ? 'border-red-500/50 focus:border-red-500' 
              : 'border-white/10 focus:border-primary/50 hover:border-white/20'
            }
            ${className}
          `}
          maxLength={maxLength}
          value={value}
          {...props}
        />
      </div>
      <div className="flex justify-between items-center px-1">
        {error ? (
          <p className="text-xs text-red-400">{error}</p>
        ) : <div />}
        
        {showCharCount && (
          <p className={`text-[10px] ${charCount > (maxLength || Infinity) ? 'text-red-400' : 'text-zinc-600'} font-mono`}>
            {charCount}{maxLength ? ` / ${maxLength}` : ''}
          </p>
        )}
      </div>
    </div>
  );
};
