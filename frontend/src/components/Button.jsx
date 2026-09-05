import React from 'react';
import { Loader2 } from 'lucide-react';

export const Button = ({
  children,
  variant = 'primary',
  size = 'md',
  isLoading = false,
  disabled = false,
  className = '',
  icon: Icon,
  type = 'button',
  onClick,
  ...props
}) => {
  const baseStyles =
    'inline-flex items-center justify-center font-medium rounded-xl transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-brand/20 disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer';

  const sizeStyles = {
    sm: 'px-3 py-1.5 text-xs gap-1.5',
    md: 'px-4 py-2 text-sm gap-2',
    lg: 'px-5 py-2.5 text-base gap-2.5',
  };

  const variantStyles = {
    primary:
      'bg-brand text-white hover:bg-brand-hover shadow-soft hover:shadow-soft-md transform hover:-translate-y-0.5 active:translate-y-0',
    secondary:
      'bg-bg-secondary text-text-primary hover:bg-border-subtle border border-border-subtle hover:border-border-hover',
    outline:
      'bg-white text-text-primary border border-border-subtle hover:border-brand hover:text-brand shadow-xs',
    ghost:
      'text-text-secondary hover:text-text-primary hover:bg-bg-secondary',
    success:
      'bg-status-success text-white hover:bg-status-success/90 shadow-soft transform hover:-translate-y-0.5',
    danger:
      'bg-status-danger text-white hover:bg-status-danger/90 shadow-soft',
  };

  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled || isLoading}
      className={`${baseStyles} ${sizeStyles[size]} ${variantStyles[variant]} ${className}`}
      {...props}
    >
      {isLoading ? (
        <>
          <Loader2 className="w-4 h-4 animate-spin text-current" />
          <span>Loading...</span>
        </>
      ) : (
        <>
          {Icon && <Icon className="w-4 h-4" />}
          {children}
        </>
      )}
    </button>
  );
};
