import React from 'react';

interface ChannelSelectorProps {
  value: string;
  onChange: (value: string) => void;
  error?: string;
}

const channels = [
  { value: 'email', label: 'Email', icon: '📧' },
  { value: 'sms', label: 'SMS', icon: '💬' },
  { value: 'push', label: 'Push Notification', icon: '🔔' },
];

export const ChannelSelector: React.FC<ChannelSelectorProps> = ({
  value,
  onChange,
  error,
}) => {
  return (
    <div>
      <label className="form-label">Channel</label>
      <div className="grid grid-cols-3 gap-4">
        {channels.map((channel) => (
          <button
            key={channel.value}
            type="button"
            onClick={() => onChange(channel.value)}
            className={`p-4 border-2 rounded-lg transition-all ${
              value === channel.value
                ? 'border-primary-500 bg-primary-900/30 text-primary-100 shadow-glow'
                : 'border-slate-700 bg-slate-800/50 text-slate-300 hover:border-primary-500/50 hover:bg-slate-800 hover:text-white'
            }`}
          >
            <div className="text-2xl mb-2">{channel.icon}</div>
            <div className="font-medium text-sm">{channel.label}</div>
          </button>
        ))}
      </div>
      {error && <p className="form-error">{error}</p>}
    </div>
  );
};
