import React from 'react';
import { Sparkles } from 'lucide-react';
import { Button } from './Button';

export const EmptyState = ({
  icon: Icon = Sparkles,
  title,
  description,
  actionText,
  onAction,
  className = '',
}) => {
  return (
    <div
      className={`bg-white rounded-2xl border border-border-subtle p-8 sm:p-12 text-center flex flex-col items-center justify-center max-w-md mx-auto shadow-soft ${className}`}
    >
      <div className="w-14 h-14 rounded-2xl bg-bg-secondary flex items-center justify-center text-text-muted mb-4 border border-border-subtle">
        <Icon className="w-7 h-7" />
      </div>
      <h3 className="text-base font-semibold text-text-primary mb-1.5">{title}</h3>
      <p className="text-xs text-text-secondary leading-relaxed mb-5">{description}</p>
      {actionText && onAction && (
        <Button variant="primary" size="md" onClick={onAction}>
          {actionText}
        </Button>
      )}
    </div>
  );
};
