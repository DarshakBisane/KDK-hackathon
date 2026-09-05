import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Target, CheckCircle2, AlertCircle, Compass, FileUp, Briefcase, Sparkles, RefreshCw, TrendingUp, ShieldCheck } from 'lucide-react';
import { skillApi, industryApi } from '../services/api';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../context/ToastContext';
import { PageHeader } from '../components/PageHeader';
import { Card } from '../components/Card';
import { ProgressBar } from '../components/ProgressBar';
import { SkillBadge } from '../components/SkillBadge';
import { Button } from '../components/Button';
import { LoadingSpinner } from '../components/LoadingSpinner';
import { EmptyState } from '../components/EmptyState';

export const SkillGapPage = () => {
  const [gapData, setGapData] = useState(null);
  const [industryInsights, setIndustryInsights] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isUpdatingIndustry, setIsUpdatingIndustry] = useState(false);

  const { user } = useAuth();
  const { showSuccess, showError } = useToast();
  const navigate = useNavigate();

  const loadAllData = async () => {
    try {
      const gapRes = await skillApi.getSkillGap();
      setGapData(gapRes.data);

      if (gapRes.data && gapRes.data.target_career_name) {
        try {
          const industryRes = await industryApi.getInsights(gapRes.data.target_career_name);
          setIndustryInsights(industryRes.data);
        } catch (err) {
          // Non-critical if insights endpoint is empty initially
        }
      }
    } catch (err) {
      showError(err.userMessage || 'Failed to calculate skill gap.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadAllData();
  }, []);

  const handleUpdateIndustrySkills = async () => {
    if (!gapData?.target_career_name) return;
    setIsUpdatingIndustry(true);
    try {
      const res = await industryApi.updateSkills(gapData.target_career_name);
      const newSkillsCount = res.data?.new_skills?.length || 0;
      const updatedReqsCount = res.data?.updated_requirements?.length || 0;

      showSuccess(
        `Industry market intelligence processed! ${res.data.jobs_processed} live postings scanned. Updated ${updatedReqsCount} career requirements.`
      );

      // Reload gap data & insights
      await loadAllData();
    } catch (err) {
      showError(err.userMessage || 'Failed to update industry skill intelligence.');
    } finally {
      setIsUpdatingIndustry(false);
    }
  };

  if (isLoading) {
    return <LoadingSpinner message="Calculating dynamic skill gap..." fullPage />;
  }

  // Handle empty state: no career selected
  if (!gapData || !gapData.target_career_name) {
    return (
      <EmptyState
        icon={Briefcase}
        title="No Target Career Selected"
        description="Choose a target role (e.g., ML Engineer, Full Stack Developer) to calculate your exact skill gap."
        actionText="Choose Target Career"
        onAction={() => navigate('/career')}
      />
    );
  }

  // Handle empty state: no resume uploaded
  if (gapData.student_skills_count === 0) {
    return (
      <EmptyState
        icon={FileUp}
        title="No Resume Analyzed Yet"
        description="Upload your resume so our AI can extract your verified skills and evaluate your readiness for your chosen role."
        actionText="Upload Resume"
        onAction={() => navigate('/resume')}
      />
    );
  }

  return (
    <div className="flex flex-col gap-8 max-w-4xl mx-auto animate-in fade-in duration-200">
      
      {/* Header */}
      <PageHeader
        title="Your Skill Gap Analysis"
        subtitle={`Dynamic market gap evaluation against the ${gapData.target_career_name} requirement profile.`}
        action={
          <Button
            variant="primary"
            size="md"
            onClick={() => navigate('/roadmap')}
            icon={Compass}
          >
            View Learning Roadmap
          </Button>
        }
      />

      {/* TOP READINESS CARD */}
      <Card className="p-6 sm:p-8 flex flex-col sm:flex-row items-center justify-between gap-6 bg-white border-border-subtle shadow-sm">
        <div className="flex flex-col gap-2 text-center sm:text-left">
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-lavender text-brand text-xs font-semibold w-fit mx-auto sm:mx-0">
            <Target className="w-3.5 h-3.5" />
            <span>Target Role: {gapData.target_career_name}</span>
          </div>
          <h2 className="text-2xl font-bold text-text-primary">
            Career Readiness: <span className="text-brand">{gapData.readiness_score}%</span>
          </h2>
          <p className="text-xs text-text-secondary max-w-md leading-relaxed">
            You match <strong>{gapData.total_matched_skills}</strong> out of{' '}
            <strong>{gapData.total_required_skills}</strong> validated industry skills required for this career track.
          </p>
          <div className="flex items-center gap-4 text-xs text-text-secondary mt-2">
            <span className="flex items-center gap-1.5">
              <span className="w-2.5 h-2.5 rounded-full bg-status-success inline-block" />
              {gapData.total_matched_skills} Matched
            </span>
            <span className="flex items-center gap-1.5">
              <span className="w-2.5 h-2.5 rounded-full bg-status-warning inline-block" />
              {gapData.missing_skills.length} Missing
            </span>
          </div>
        </div>

        {/* Circular Progress Gauge */}
        <ProgressBar
          variant="circular"
          progress={gapData.readiness_score}
          className="flex-shrink-0"
        />
      </Card>

      {/* PHASE 2: DYNAMIC INDUSTRY SKILL INTELLIGENCE CARD */}
      <Card className="p-6 border-brand/20 bg-gradient-to-br from-white via-indigo-50/20 to-lavender/10 shadow-sm">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 pb-4 border-b border-border-subtle">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-brand text-white flex items-center justify-center shadow-sm">
              <Sparkles className="w-5 h-5" />
            </div>
            <div>
              <h3 className="font-bold text-base text-text-primary flex items-center gap-2">
                Dynamic Industry Skill Intelligence
                <span className="text-[10px] px-2 py-0.5 rounded-full bg-mint text-mint-text font-semibold uppercase tracking-wider">
                  Live Market
                </span>
              </h3>
              <p className="text-xs text-text-secondary">
                Requirements automatically evolve based on verified job market postings & AI evidence.
              </p>
            </div>
          </div>

          <Button
            variant="secondary"
            size="sm"
            onClick={handleUpdateIndustrySkills}
            disabled={isUpdatingIndustry}
            icon={RefreshCw}
            className="flex-shrink-0 bg-white hover:bg-slate-50 border-brand/30 text-brand"
          >
            {isUpdatingIndustry ? 'Processing Job Postings...' : 'Update Industry Skills'}
          </Button>
        </div>

        {/* Market Insights Breakdown */}
        {industryInsights && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-5">
            {/* Validated Required Skills */}
            <div className="p-4 rounded-xl bg-white border border-border-subtle">
              <div className="flex items-center justify-between mb-3">
                <span className="text-xs font-bold text-text-primary flex items-center gap-1.5">
                  <ShieldCheck className="w-4 h-4 text-brand" />
                  Validated Market Requirements
                </span>
                <span className="text-[11px] font-semibold text-text-secondary">
                  {industryInsights.required_skills?.length || 0} skills
                </span>
              </div>
              <div className="flex flex-wrap gap-1.5 max-h-36 overflow-y-auto">
                {industryInsights.required_skills?.map((s) => (
                  <span
                    key={s.name}
                    className="text-xs px-2.5 py-1 rounded-lg bg-slate-100 text-slate-800 font-medium flex items-center gap-1"
                  >
                    {s.name}
                    <span className="text-[10px] text-text-secondary opacity-75">
                      ({Math.round((s.confidence || 0.9) * 100)}%)
                    </span>
                  </span>
                ))}
              </div>
            </div>

            {/* Emerging Skills */}
            <div className="p-4 rounded-xl bg-white border border-border-subtle">
              <div className="flex items-center justify-between mb-3">
                <span className="text-xs font-bold text-text-primary flex items-center gap-1.5">
                  <TrendingUp className="w-4 h-4 text-emerald-600" />
                  Emerging Industry Trends
                </span>
                <span className="text-[11px] font-semibold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded-md">
                  {industryInsights.emerging_skills?.length || 0} candidate skills
                </span>
              </div>
              {industryInsights.emerging_skills && industryInsights.emerging_skills.length > 0 ? (
                <div className="flex flex-wrap gap-1.5 max-h-36 overflow-y-auto">
                  {industryInsights.emerging_skills.map((s) => (
                    <span
                      key={s.name}
                      className="text-xs px-2.5 py-1 rounded-lg bg-emerald-50 text-emerald-800 border border-emerald-200/50 font-medium flex items-center gap-1.5"
                    >
                      <span>{s.name}</span>
                      <span className="text-[10px] font-bold px-1.5 py-0.2 bg-emerald-200/60 rounded text-emerald-900">
                        {s.mention_count} postings
                      </span>
                    </span>
                  ))}
                </div>
              ) : (
                <p className="text-xs text-text-secondary italic py-3">
                  Click 'Update Industry Skills' to scan live job postings for emerging trends.
                </p>
              )}
            </div>
          </div>
        )}
      </Card>

      {/* 2 MAIN SECTIONS: YOU ALREADY HAVE & SKILLS TO DEVELOP */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        
        {/* You Already Have */}
        <Card className="p-6 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between pb-3 border-b border-border-subtle mb-4">
              <div className="flex items-center gap-2">
                <div className="w-7 h-7 rounded-lg bg-mint text-mint-text flex items-center justify-center font-bold text-xs">
                  <CheckCircle2 className="w-4 h-4" />
                </div>
                <h3 className="font-bold text-sm text-text-primary">You Already Have</h3>
              </div>
              <span className="text-xs font-semibold px-2 py-0.5 rounded-md bg-mint text-mint-text">
                {gapData.matched_skills.length} skills
              </span>
            </div>

            {gapData.matched_skills.length > 0 ? (
              <div className="flex flex-wrap gap-2">
                {gapData.matched_skills.map((skill) => (
                  <SkillBadge key={skill} name={skill} type="matched" />
                ))}
              </div>
            ) : (
              <p className="text-xs text-text-secondary italic py-4">
                No matching skills found yet for this specific career track.
              </p>
            )}
          </div>

          <div className="mt-6 pt-3 border-t border-border-subtle text-[11px] text-text-secondary">
            Verified from your resume extraction
          </div>
        </Card>

        {/* Skills to Develop */}
        <Card className="p-6 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between pb-3 border-b border-border-subtle mb-4">
              <div className="flex items-center gap-2">
                <div className="w-7 h-7 rounded-lg bg-amber-50 text-amber-800 flex items-center justify-center font-bold text-xs">
                  <AlertCircle className="w-4 h-4" />
                </div>
                <h3 className="font-bold text-sm text-text-primary">Skills to Develop</h3>
              </div>
              <span className="text-xs font-semibold px-2 py-0.5 rounded-md bg-amber-50 text-amber-800">
                {gapData.missing_skills.length} missing
              </span>
            </div>

            {gapData.missing_skills.length > 0 ? (
              <div className="flex flex-wrap gap-2">
                {gapData.missing_skills.map((item) => (
                  <SkillBadge
                    key={item.name}
                    name={item.name}
                    type="missing"
                    importance={item.importance}
                  />
                ))}
              </div>
            ) : (
              <div className="text-center py-6 bg-mint-light/40 rounded-xl p-4">
                <p className="text-xs font-bold text-mint-text">100% Core Requirements Met!</p>
                <p className="text-[11px] text-text-secondary mt-1">
                  You possess all standard skills required for this career path.
                </p>
              </div>
            )}
          </div>

          <div className="mt-6 pt-3 border-t border-border-subtle flex items-center justify-between text-[11px] text-text-secondary">
            <span>Prioritized by role importance</span>
            <button
              onClick={() => navigate('/roadmap')}
              className="text-brand font-semibold hover:underline"
            >
              Start Roadmap →
            </button>
          </div>
        </Card>

      </div>

    </div>
  );
};
