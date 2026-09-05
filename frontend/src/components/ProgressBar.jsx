import React from 'react';

export const ProgressBar = ({
  progress = 0,
  variant = 'linear',
  size = 'md',
  showLabel = true,
  label = '',
  className = '',
}) => {
  const clampedProgress = Math.min(100, Math.max(0, Number(progress) || 0));

  // Determine color theme based on score
  const getProgressColor = (val) => {
    if (val >= 75) return 'bg-status-success';
    if (val >= 40) return 'bg-brand';
    return 'bg-status-warning';
  };

  const getStrokeColor = (val) => {
    if (val >= 75) return '#35A76F';
    if (val >= 40) return '#6C63FF';
    return '#E7A83B';
  };

  if (variant === 'circular') {
    const radius = 48;
    const circumference = 2 * Math.PI * radius;
    const offset = circumference - (clampedProgress / 100) * circumference;

    return (
      <div className={`relative inline-flex items-center justify-center ${className}`}>
        <svg className="w-28 h-28 transform -rotate-90">
          <circle
            cx="56"
            cy="56"
            r={radius}
            stroke="#E4E7EC"
            strokeWidth="8"
            fill="transparent"
          />
          <circle
            cx="56"
            cy="56"
            r={radius}
            stroke={getStrokeColor(clampedProgress)}
            strokeWidth="8"
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            strokeLinecap="round"
            fill="transparent"
            className="transition-all duration-700 ease-out"
          />
        </svg>
        <div className="absolute flex flex-col items-center justify-center text-center">
          <span className="text-2xl font-bold text-text-primary tracking-tight">
            {clampedProgress}%
          </span>
          <span className="text-[10px] font-medium text-text-secondary">Readiness</span>
        </div>
      </div>
    );
  }

  const heightStyles = {
    sm: 'h-1.5',
    md: 'h-2.5',
    lg: 'h-3.5',
  };

  return (
    <div className={`w-full flex flex-col gap-1.5 ${className}`}>
      {(showLabel || label) && (
        <div className="flex items-center justify-between text-xs font-medium">
          <span className="text-text-secondary">{label}</span>
          <span className="text-text-primary font-semibold">{clampedProgress}%</span>
        </div>
      )}
      <div className={`w-full bg-bg-secondary rounded-full overflow-hidden border border-border-subtle ${heightStyles[size]}`}>
        <div
          className={`${heightStyles[size]} ${getProgressColor(clampedProgress)} rounded-full transition-all duration-500 ease-out`}
          style={{ width: `${clampedProgress}%` }}
        />
      </div>
    </div>
  );
};
