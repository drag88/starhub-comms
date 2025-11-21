import React from 'react';

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
}

export const Input: React.FC<InputProps> = ({
  label,
  error,
  className = '',
  ...props
}) => {
  return (
    <div className="w-full space-y-1.5">
      {label && (
        <label className="text-[10px] font-bold text-zinc-400 uppercase tracking-wider block ml-1">
          {label}
        </label>
      )}
      <div className="relative group">
        <div className="absolute -inset-0.5 bg-gradient-to-r from-primary/20 to-blue-500/20 rounded-lg blur opacity-0 group-focus-within:opacity-100 transition duration-500" />
        <input
          className={`
            relative w-full bg-zinc-900/80 border rounded-lg px-4 py-2.5 text-sm text-zinc-200 placeholder:text-zinc-600 
            transition-all duration-200
            focus:outline-none focus:ring-1 focus:ring-primary/50
            ${error 
              ? 'border-red-500/50 focus:border-red-500' 
              : 'border-white/10 focus:border-primary/50 hover:border-white/20'
            }
            ${className}
          `}
          {...props}
        />
      </div>
      {error && (
        <p className="text-xs text-red-400 ml-1">{error}</p>
      )}
    </div>
  );
};
