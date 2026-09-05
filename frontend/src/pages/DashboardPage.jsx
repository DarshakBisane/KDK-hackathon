import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Target,
  CheckCircle2,
  AlertCircle,
  TrendingUp,
  Compass,
  ArrowRight,
  Sparkles,
  FileUp,
  Briefcase,
  Layers
} from 'lucide-react';
import { dashboardApi } from '../services/api';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../context/ToastContext';
import { PageHeader } from '../components/PageHeader';
import { Card } from '../components/Card';
import { ProgressBar } from '../components/ProgressBar';
import { SkillBadge } from '../components/SkillBadge';
import { Button } from '../components/Button';
import { LoadingSpinner } from '../components/LoadingSpinner';
import { EmptyState } from '../components/EmptyState';

export const DashboardPage = () => {
  const [data, setData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  const { user } = useAuth();
  const { showError } = useToast();
  const navigate = useNavigate();

  useEffect(() => {
    const fetchDashboard = async () => {
      try {
        const response = await dashboardApi.getDashboardData();
        setData(response.data);
      } catch (err) {
        showError(err.userMessage || 'Failed to load dashboard data.');
      } finally {
        setIsLoading(false);
      }
    };
    fetchDashboard();
  }, [showError]);

  if (isLoading) {
    return <LoadingSpinner message="Loading your career insights..." fullPage />;
  }

  // Handle first-time user empty state (no career or no resume)
  if (!data?.target_career_name) {
    return (
      <div className="max-w-3xl mx-auto py-6">
        <PageHeader
          title={`Welcome back, ${user?.name?.split(' ')[0] || 'Student'} 👋`}
          subtitle="Let's set up your career track to get personalized skill gap intelligence."
        />
        <EmptyState
          icon={Briefcase}
          title="Select Your Target Career Track"
          description="Choose from 10 industry roles such as ML Engineer, Backend Developer, or Cloud Architect to calculate your readiness score."
          actionText="Select Career Track"
          onAction={() => navigate('/career')}
        />
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-8 animate-in fade-in duration-200">
      
      {/* 1. WELCOME HEADER */}
      <PageHeader
        title={`Welcome back, ${data.user_name?.split(' ')[0] || 'Student'} 👋`}
        subtitle="Here is your current career readiness and skill gap overview."
        badge={data.student_status}
        action={
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => navigate('/resume')}
              icon={FileUp}
            >
              Update Resume
            </Button>
            <Button
              variant="primary"
              size="sm"
              onClick={() => navigate('/roadmap')}
              icon={Compass}
            >
              Learning Roadmap
            </Button>
          </div>
        }
      />

      {/* 2. MAIN READINESS CARD + 3 METRIC CARDS */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
        
        {/* Main Readiness Gauge (Span 2 cols on lg) */}
        <Card className="lg:col-span-2 p-6 sm:p-7 flex flex-col justify-between bg-white border-border-subtle">
          <div>
            <div className="flex items-center justify-between mb-4">
              <span className="text-xs font-semibold px-2.5 py-1 rounded-full bg-lavender text-brand border border-lavender-text/20">
                Target Role
              </span>
              <button
                onClick={() => navigate('/career')}
                className="text-xs font-semibold text-brand hover:underline"
              >
                Change Career Track
              </button>
            </div>

            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
              <div>
                <h2 className="text-2xl sm:text-3xl font-bold text-text-primary">
                  {data.target_career_name}
                </h2>
                <p className="text-xs text-text-secondary mt-1">
                  Overall Career Readiness based on {data.strong_skills_count + data.missing_skills_count} core requirements
                </p>
              </div>
              <div className="text-right sm:text-right">
                <span className="text-3xl font-extrabold text-brand tracking-tight">
                  {data.readiness_score}%
                </span>
              </div>
            </div>
          </div>

          <div className="mt-6 pt-4 border-t border-border-subtle">
            <ProgressBar
              progress={data.readiness_score}
              size="md"
              showLabel={false}
            />
            <div className="flex items-center justify-between text-[11px] text-text-secondary mt-2">
              <span>{data.strong_skills_count} skills mastered</span>
              <span>{data.missing_skills_count} skills remaining</span>
            </div>
          </div>
        </Card>

        {/* 3 Quick Stat Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-3 lg:grid-cols-1 gap-3">
          
          <Card className="p-4 flex items-center justify-between bg-mint-light/40 border-mint-text/20">
            <div>
              <p className="text-xs text-text-secondary font-medium">Strong Skills</p>
              <p className="text-xl font-bold text-text-primary mt-0.5">{data.strong_skills_count}</p>
            </div>
            <div className="w-10 h-10 rounded-xl bg-mint text-mint-text flex items-center justify-center">
              <CheckCircle2 className="w-5 h-5" />
            </div>
          </Card>

          <Card className="p-4 flex items-center justify-between bg-lavender/40 border-lavender-text/20">
            <div>
              <p className="text-xs text-text-secondary font-medium">Missing Skills</p>
              <p className="text-xl font-bold text-text-primary mt-0.5">{data.missing_skills_count}</p>
            </div>
            <div className="w-10 h-10 rounded-xl bg-lavender text-brand flex items-center justify-center">
              <AlertCircle className="w-5 h-5" />
            </div>
          </Card>

          <Card className="p-4 flex items-center justify-between bg-amber-50/70 border-amber-200">
            <div>
              <p className="text-xs text-text-secondary font-medium">Critical Gaps</p>
              <p className="text-xl font-bold text-amber-900 mt-0.5">{data.critical_gaps_count}</p>
            </div>
            <div className="w-10 h-10 rounded-xl bg-amber-100 text-amber-800 flex items-center justify-center">
              <Target className="w-5 h-5" />
            </div>
          </Card>

        </div>

      </div>

      {/* 3. SKILL OVERVIEW & ACTIONABLE NEXT STEPS */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Skill Overview (2 cols) */}
        <Card className="lg:col-span-2 p-6 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between pb-3 border-b border-border-subtle mb-4">
              <h3 className="font-bold text-sm text-text-primary">Skills Breakdown</h3>
              <button
                onClick={() => navigate('/skills')}
                className="text-xs font-semibold text-brand hover:underline"
              >
                View Full Gap →
              </button>
            </div>

            {/* Matched skills */}
            <div className="mb-5">
              <p className="text-xs font-semibold text-text-secondary mb-2 flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full bg-status-success" />
                Matched Skills ({data.matched_skills.length})
              </p>
              {data.matched_skills.length > 0 ? (
                <div className="flex flex-wrap gap-2">
                  {data.matched_skills.map((s) => (
                    <SkillBadge key={s} name={s} type="matched" />
                  ))}
                </div>
              ) : (
                <p className="text-xs text-text-secondary italic">None detected yet from resume.</p>
              )}
            </div>

            {/* Missing skills */}
            <div>
              <p className="text-xs font-semibold text-text-secondary mb-2 flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full bg-status-warning" />
                Missing Skills to Bridge ({data.missing_skills.length})
              </p>
              {data.missing_skills.length > 0 ? (
                <div className="flex flex-wrap gap-2">
                  {data.missing_skills.map((item) => (
                    <SkillBadge
                      key={item.name}
                      name={item.name}
                      type="missing"
                      importance={item.importance}
                    />
                  ))}
                </div>
              ) : (
                <p className="text-xs text-mint-text font-semibold">All core skills covered!</p>
              )}
            </div>
          </div>

          <div className="mt-6 pt-4 border-t border-border-subtle flex justify-end">
            <Button
              variant="outline"
              size="sm"
              onClick={() => navigate('/skills')}
              icon={ArrowRight}
            >
              Analyze Full Skill Gap
            </Button>
          </div>
        </Card>

        {/* Next Steps (1 col) */}
        <Card className="p-6 flex flex-col justify-between bg-white border-border-subtle">
          <div>
            <div className="flex items-center gap-2 pb-3 border-b border-border-subtle mb-4">
              <div className="w-6 h-6 rounded-lg bg-brand-light text-brand flex items-center justify-center font-bold text-xs">
                <Sparkles className="w-3.5 h-3.5" />
              </div>
              <h3 className="font-bold text-sm text-text-primary">Recommended Next Steps</h3>
            </div>

            <div className="flex flex-col gap-3">
              {data.next_steps && data.next_steps.map((step, idx) => (
                <div
                  key={idx}
                  className="p-3 bg-bg-secondary rounded-xl border border-border-subtle flex items-start gap-2.5 text-xs text-text-primary leading-relaxed"
                >
                  <span className="w-5 h-5 rounded-md bg-white text-brand font-bold text-[10px] flex items-center justify-center flex-shrink-0 border border-border-subtle shadow-xs">
                    {idx + 1}
                  </span>
                  <span>{step}</span>
                </div>
              ))}
            </div>
          </div>

          <div className="mt-6 pt-4 border-t border-border-subtle">
            <Button
              variant="primary"
              size="md"
              onClick={() => navigate('/roadmap')}
              icon={Compass}
              className="w-full"
            >
              Follow Learning Roadmap
            </Button>
          </div>
        </Card>

      </div>

    </div>
  );
};
