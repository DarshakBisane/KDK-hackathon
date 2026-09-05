import React from 'react';
import {
  Brain,
  BarChart3,
  LineChart,
  Sparkles,
  Server,
  Layout,
  Layers,
  Cloud,
  Cpu,
  ShieldCheck,
  Briefcase,
  CheckCircle2
} from 'lucide-react';

const ICON_MAP = {
  Brain,
  BarChart3,
  LineChart,
  Sparkles,
  Server,
  Layout,
  Layers,
  Cloud,
  Cpu,
  ShieldCheck,
  Briefcase,
};

export const CareerCard = ({
  career,
  isSelected = false,
  onSelect,
  className = '',
}) => {
  const IconComponent = ICON_MAP[career.icon] || Briefcase;
  const skillsCount = career.required_skills ? career.required_skills.length : 0;

  return (
    <div
      onClick={() => onSelect && onSelect(career)}
      className={`group relative p-5 rounded-2xl border transition-all duration-200 cursor-pointer flex flex-col justify-between ${
        isSelected
          ? 'bg-lavender/40 border-brand shadow-soft-md ring-2 ring-brand/20'
          : 'bg-white border-border-subtle hover:border-brand/40 hover:shadow-soft-md hover:-translate-y-1'
      } ${className}`}
    >
      <div>
        {/* Card Header: Icon + Category */}
        <div className="flex items-center justify-between mb-3.5">
          <div
            className={`w-10 h-10 rounded-xl flex items-center justify-center transition-colors ${
              isSelected
                ? 'bg-brand text-white shadow-soft'
                : 'bg-bg-secondary text-brand group-hover:bg-brand-light'
            }`}
          >
            <IconComponent className="w-5 h-5" />
          </div>
          {isSelected ? (
            <span className="flex items-center gap-1 text-xs font-semibold text-brand bg-white px-2.5 py-1 rounded-full border border-brand/20">
              <CheckCircle2 className="w-3.5 h-3.5" /> Selected
            </span>
          ) : (
            <span className="text-[11px] font-medium text-text-secondary bg-bg-secondary px-2.5 py-1 rounded-full border border-border-subtle">
              {career.category || 'Engineering'}
            </span>
          )}
        </div>

        {/* Title & Description */}
        <h3 className="font-semibold text-base text-text-primary group-hover:text-brand transition-colors mb-1.5">
          {career.name}
        </h3>
        <p className="text-xs text-text-secondary leading-relaxed line-clamp-2 mb-4">
          {career.description}
        </p>
      </div>

      {/* Footer: Skills count */}
      <div className="pt-3 border-t border-border-subtle flex items-center justify-between text-xs text-text-secondary">
        <span>Required Skills</span>
        <span className="font-semibold text-text-primary bg-bg-secondary px-2 py-0.5 rounded-lg border border-border-subtle">
          {skillsCount} skills
        </span>
      </div>
    </div>
  );
};
