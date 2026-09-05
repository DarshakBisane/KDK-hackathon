import React from 'react';
import { Loader2 } from 'lucide-react';

export const LoadingSpinner = ({
  message = 'Loading...',
  fullPage = false,
  className = '',
}) => {
  const content = (
    <div className={`flex flex-col items-center justify-center gap-3 py-12 ${className}`}>
      <div className="w-10 h-10 rounded-xl bg-brand-light flex items-center justify-center text-brand shadow-soft">
        <Loader2 className="w-5 h-5 animate-spin" />
      </div>
      <p className="text-sm font-medium text-text-secondary animate-pulse">{message}</p>
    </div>
  );

  if (fullPage) {
    return (
      <div className="min-h-[60vh] flex items-center justify-center">
        {content}
      </div>
    );
  }

  return content;
};
