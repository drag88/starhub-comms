import React, { useState, useEffect } from 'react';
import type { Communication } from '/Users/asreenivas/Library/CloudStorage/OneDrive-StarHubLtd/02_Data_Analytics/Scripts/29. Customer Comms Generator/frontend/src/types/communication';
import { Textarea } from '/Users/asreenivas/Library/CloudStorage/OneDrive-StarHubLtd/02_Data_Analytics/Scripts/29. Customer Comms Generator/frontend/src/components/shared/Textarea';
import { Button } from '/Users/asreenivas/Library/CloudStorage/OneDrive-StarHubLtd/02_Data_Analytics/Scripts/29. Customer Comms Generator/frontend/src/components/shared/Button';
import { communicationAPI } from '/Users/asreenivas/Library/CloudStorage/OneDrive-StarHubLtd/02_Data_Analytics/Scripts/29. Customer Comms Generator/frontend/src/services/api';

interface EditModalProps {
  communication: Communication;
  channel: string;
  onClose: () => void;
  onSave: () => void;
}

const channelLimits: Record<string, { chars: number; label: string }> = {
  sms: { chars: 160, label: 'SMS' },
  email: { chars: 60, label: 'Email Subject' },
  push: { chars: 170, label: 'Push Notification' }, // 50 title + 120 body
};

export const EditModal: React.FC<EditModalProps> = ({
  communication,
  channel,
  onClose,
  onSave,
}) => {
  const [editedText, setEditedText] = useState(
    communication.edited_text || communication.communication_text
  );
  const [saving, setSaving] = useState(false);

  const limit = channelLimits[channel];
  const isOverLimit = limit && editedText.length > limit.chars;

  const handleSave = async () => {
    setSaving(true);
    try {
      await communicationAPI.update(communication.communication_id, {
        edited_text: editedText,
      });
      onSave();
      onClose();
    } catch (error) {
      console.error('Failed to save edit:', error);
    } finally {
      setSaving(false);
    }
  };

  useEffect(() => {
    // Prevent body scroll when modal is open
    document.body.style.overflow = 'hidden';
    return () => {
      document.body.style.overflow = 'unset';
    };
  }, []);

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div className="p-6">
          <div className="flex justify-between items-start mb-4">
            <h2 className="text-xl font-bold">Edit Communication</h2>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600 text-2xl leading-none"
            >
              ×
            </button>
          </div>

          <div className="mb-4">
            <div className="flex justify-between items-center mb-2">
              <label className="form-label mb-0">Communication Text</label>
              {limit && (
                <span className={`text-sm font-medium ${isOverLimit ? 'text-danger' : 'text-gray-600'}`}>
                  {editedText.length} / {limit.chars} characters
                </span>
              )}
            </div>
            <Textarea
              value={editedText}
              onChange={(e) => setEditedText(e.target.value)}
              rows={8}
              className="font-mono text-sm"
            />
            {isOverLimit && (
              <p className="text-danger text-sm mt-2">
                ⚠️ Exceeds recommended {limit.label} character limit ({limit.chars} chars)
              </p>
            )}
          </div>

          <div className="rounded-lg p-4 mb-4" style={{ backgroundColor: '#e6f5ed' }}>
            <h4 className="text-sm font-semibold mb-2" style={{ color: '#002110' }}>Original Text</h4>
            <p className="text-sm whitespace-pre-wrap" style={{ color: '#004220' }}>
              {communication.communication_text}
            </p>
          </div>

          <div className="flex justify-end gap-3">
            <Button variant="secondary" onClick={onClose}>
              Cancel
            </Button>
            <Button
              variant="primary"
              onClick={handleSave}
              loading={saving}
              disabled={!editedText.trim()}
            >
              Save Changes
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
};
