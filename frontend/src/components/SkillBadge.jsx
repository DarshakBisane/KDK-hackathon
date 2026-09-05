import React from 'react';
import { Check, AlertCircle } from 'lucide-react';

export const SkillBadge = ({
  name,
  type = 'neutral', // 'matched', 'missing', 'neutral'
  importance = null, // 'HIGH', 'MEDIUM', 'LOW'
  size = 'md',
  className = '',
}) => {
  const sizeStyles = {
    sm: 'px-2.5 py-1 text-xs gap-1.5',
    md: 'px-3 py-1.5 text-xs gap-2',
    lg: 'px-3.5 py-2 text-sm gap-2',
  };

  const typeStyles = {
    matched: 'bg-mint text-mint-text border-mint-text/20 font-medium',
    missing:
      importance === 'HIGH'
        ? 'bg-amber-50 text-amber-800 border-amber-200/80 font-medium'
        : 'bg-lavender text-lavender-dark border-lavender-text/20 font-medium',
    neutral: 'bg-bg-secondary text-text-primary border-border-subtle hover:border-border-hover',
  };

  return (
    <span
      className={`inline-flex items-center rounded-xl border transition-all ${sizeStyles[size]} ${typeStyles[type]} ${className}`}
    >
      {type === 'matched' && <Check className="w-3.5 h-3.5 text-status-success flex-shrink-0" />}
      {type === 'missing' && <AlertCircle className="w-3.5 h-3.5 text-status-warning flex-shrink-0" />}
      <span>{name}</span>
      {importance && type === 'missing' && (
        <span
          className={`text-[10px] uppercase font-bold tracking-wider px-1.5 py-0.5 rounded-md ${
            importance === 'HIGH'
              ? 'bg-status-warning/20 text-amber-900'
              : 'bg-lavender-text/10 text-lavender-dark'
          }`}
        >
          {importance}
        </span>
      )}
    </span>
  );
};
