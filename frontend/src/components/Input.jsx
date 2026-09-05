import React from 'react';

export const Input = ({
  label,
  error,
  helperText,
  id,
  type = 'text',
  className = '',
  required = false,
  ...props
}) => {
  const inputId = id || (label ? label.toLowerCase().replace(/\s+/g, '-') : undefined);

  return (
    <div className="flex flex-col gap-1.5 w-full">
      {label && (
        <label
          htmlFor={inputId}
          className="text-xs font-semibold text-text-primary flex items-center gap-1"
        >
          {label}
          {required && <span className="text-status-danger">*</span>}
        </label>
      )}
      <input
        id={inputId}
        type={type}
        required={required}
        className={`w-full px-3.5 py-2.5 bg-white rounded-xl border text-sm text-text-primary placeholder:text-text-muted transition-all duration-150 focus:outline-none focus:ring-2 focus:ring-brand/20 focus:border-brand ${
          error
            ? 'border-status-danger focus:ring-status-danger/20 focus:border-status-danger'
            : 'border-border-subtle hover:border-border-hover'
        } ${className}`}
        {...props}
      />
      {error && <span className="text-xs text-status-danger font-medium">{error}</span>}
      {helperText && !error && (
        <span className="text-xs text-text-secondary">{helperText}</span>
      )}
    </div>
  );
};
