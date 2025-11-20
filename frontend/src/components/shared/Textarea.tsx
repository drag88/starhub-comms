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
    <div className="w-full">
      {label && (
        <label className="form-label">
          {label}
        </label>
      )}
      <textarea
        className={`input-field ${error ? 'border-danger' : ''} ${className}`}
        maxLength={maxLength}
        value={value}
        {...props}
      />
      <div className="flex justify-between items-center mt-1">
        {error && (
          <p className="form-error">{error}</p>
        )}
        {showCharCount && (
          <p className={`text-sm ${charCount > (maxLength || Infinity) ? 'text-danger' : 'text-slate-500'} ml-auto`}>
            {charCount}{maxLength ? `/${maxLength}` : ''} characters
          </p>
        )}
      </div>
    </div>
  );
};
