import React from 'react';
import { ChevronDown } from 'lucide-react';

interface SelectOption {
  value: string;
  label: string;
}

interface SelectProps extends React.SelectHTMLAttributes<HTMLSelectElement> {
  label?: string;
  error?: string;
  options: SelectOption[];
}

export const Select: React.FC<SelectProps> = ({
  label,
  error,
  options,
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
        <select
          className={`
            relative w-full bg-zinc-900/80 border rounded-lg px-4 py-2.5 text-sm text-zinc-200 
            appearance-none cursor-pointer
            transition-all duration-200
            focus:outline-none focus:ring-1 focus:ring-primary/50
            ${error 
              ? 'border-red-500/50 focus:border-red-500' 
              : 'border-white/10 focus:border-primary/50 hover:border-white/20'
            }
            ${className}
          `}
          {...props}
        >
          <option value="" className="bg-zinc-900 text-zinc-500">Select option...</option>
          {options.map((option) => (
            <option key={option.value} value={option.value} className="bg-zinc-900 text-zinc-200">
              {option.label}
            </option>
          ))}
        </select>
        <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-500 pointer-events-none group-hover:text-zinc-300" />
      </div>
      {error && (
        <p className="text-xs text-red-400 ml-1">{error}</p>
      )}
    </div>
  );
};
