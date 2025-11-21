import React from 'react';
import { Mail, MessageSquare, Bell } from 'lucide-react';

interface ChannelSelectorProps {
  value: string;
  onChange: (value: string) => void;
  error?: string;
}

const channels = [
  { value: 'email', label: 'Email', icon: Mail },
  { value: 'sms', label: 'SMS', icon: MessageSquare },
  { value: 'push', label: 'Push Notification', icon: Bell },
];

export const ChannelSelector: React.FC<ChannelSelectorProps> = ({
  value,
  onChange,
  error,
}) => {
  return (
    <div className="w-full">
      <label className="text-sm font-medium text-zinc-400 mb-2 block uppercase tracking-wider text-[10px]">
        Select Channel
      </label>
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        {channels.map((channel) => {
          const isSelected = value === channel.value;
          const Icon = channel.icon;
          return (
            <button
              key={channel.value}
              type="button"
              onClick={() => onChange(channel.value)}
              className={`
                relative p-4 rounded-lg transition-all duration-200 border text-left group overflow-hidden
                ${isSelected
                  ? 'border-primary bg-primary/10 text-white shadow-[0_0_15px_rgba(0,166,81,0.2)]'
                  : 'border-zinc-800 bg-zinc-900/50 text-zinc-400 hover:border-zinc-600 hover:bg-zinc-800 hover:text-zinc-200'
                }
              `}
            >
              {isSelected && (
                <div className="absolute top-0 left-0 w-1 h-full bg-primary" />
              )}
              <div className={`mb-3 ${isSelected ? 'text-primary' : 'text-zinc-500 group-hover:text-zinc-300'}`}>
                <Icon className="w-6 h-6" />
              </div>
              <div className="font-semibold text-sm tracking-wide">
                {channel.label}
              </div>
            </button>
          );
        })}
      </div>
      {error && <p className="mt-1.5 text-xs text-red-400">{error}</p>}
    </div>
  );
};
