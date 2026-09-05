import React from 'react';

export const PageHeader = ({
  title,
  subtitle,
  badge,
  action,
  className = '',
}) => {
  return (
    <div className={`flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8 ${className}`}>
      <div>
        <div className="flex items-center gap-2.5 mb-1">
          <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-text-primary">
            {title}
          </h1>
          {badge && (
            <span className="text-xs font-semibold px-2.5 py-0.5 rounded-full bg-lavender text-brand border border-lavender-text/20">
              {badge}
            </span>
          )}
        </div>
        {subtitle && (
          <p className="text-sm text-text-secondary leading-relaxed">
            {subtitle}
          </p>
        )}
      </div>
      {action && <div className="flex-shrink-0">{action}</div>}
    </div>
  );
};
