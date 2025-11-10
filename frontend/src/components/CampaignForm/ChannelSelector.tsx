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
                ? 'border-primary-600 bg-primary-50'
                : 'border-gray-300 bg-white hover:border-primary-300'
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
