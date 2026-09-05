import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Compass,
  CheckCircle2,
  Clock,
  Circle,
  Briefcase,
  FileUp,
  Sparkles,
  ArrowRight
} from 'lucide-react';
import { roadmapApi } from '../services/api';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../context/ToastContext';
import { PageHeader } from '../components/PageHeader';
import { Card } from '../components/Card';
import { ProgressBar } from '../components/ProgressBar';
import { Button } from '../components/Button';
import { LoadingSpinner } from '../components/LoadingSpinner';
import { EmptyState } from '../components/EmptyState';

export const RoadmapPage = () => {
  const [roadmapData, setRoadmapData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [updatingId, setUpdatingId] = useState(null);

  const { user } = useAuth();
  const { showSuccess, showError } = useToast();
  const navigate = useNavigate();

  useEffect(() => {
    const fetchRoadmap = async () => {
      try {
        const response = await roadmapApi.getRoadmap();
        setRoadmapData(response.data);
      } catch (err) {
        showError(err.userMessage || 'Failed to load learning roadmap.');
      } finally {
        setIsLoading(false);
      }
    };
    fetchRoadmap();
  }, [showError]);

  const handleStatusChange = async (itemId, newStatus) => {
    setUpdatingId(itemId);
    try {
      const response = await roadmapApi.updateItemStatus(itemId, newStatus);
      setRoadmapData(response.data);
      showSuccess(`Status updated to "${newStatus}"!`);
    } catch (err) {
      showError(err.userMessage || 'Failed to update milestone status.');
    } finally {
      setUpdatingId(null);
    }
  };

  if (isLoading) {
    return <LoadingSpinner message="Preparing your personalized roadmap..." fullPage />;
  }

  // Handle empty state: no career chosen
  if (!user?.target_career_id) {
    return (
      <EmptyState
        icon={Briefcase}
        title="Select a Target Career First"
        description="Choose a target career track so we can identify your missing skills and generate your custom weekly roadmap."
        actionText="Select Career"
        onAction={() => navigate('/career')}
      />
    );
  }

  // Handle empty state: no missing skills (e.g. 100% matched or no items)
  if (!roadmapData || roadmapData.total_items === 0) {
    return (
      <div className="max-w-2xl mx-auto py-8">
        <Card className="p-8 text-center flex flex-col items-center">
          <div className="w-14 h-14 rounded-2xl bg-mint text-mint-text flex items-center justify-center mb-4">
            <CheckCircle2 className="w-8 h-8" />
          </div>
          <h2 className="text-xl font-bold text-text-primary mb-2">No Missing Skills Detected!</h2>
          <p className="text-xs text-text-secondary max-w-md mb-6 leading-relaxed">
            You already match 100% of the core required skills for <strong>{user?.target_career_name}</strong>.
            Keep building end-to-end portfolio projects to solidify your practical expertise.
          </p>
          <Button variant="primary" size="md" onClick={() => navigate('/dashboard')} icon={ArrowRight}>
            Back to Dashboard
          </Button>
        </Card>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-8 max-w-4xl mx-auto animate-in fade-in duration-200">
      
      {/* 1. HEADER */}
      <PageHeader
        title="Your Learning Roadmap"
        subtitle={`Step-by-step weekly milestone plan to achieve 100% readiness for ${user?.target_career_name || 'your target career'}.`}
        action={
          <Button
            variant="outline"
            size="sm"
            onClick={() => navigate('/skills')}
          >
            View Skill Gap
          </Button>
        }
      />

      {/* 2. PROGRESS OVERVIEW CARD */}
      <Card className="p-6 bg-white border-border-subtle shadow-soft">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-4">
          <div>
            <span className="text-xs font-semibold uppercase tracking-wider text-text-muted">
              Roadmap Progress
            </span>
            <h2 className="text-lg font-bold text-text-primary mt-0.5">
              {roadmapData.completed_items} of {roadmapData.total_items} Milestones Completed
            </h2>
          </div>
          <span className="text-2xl font-extrabold text-brand">
            {roadmapData.progress_percentage}%
          </span>
        </div>

        <ProgressBar
          progress={roadmapData.progress_percentage}
          size="md"
          showLabel={false}
        />

        <div className="grid grid-cols-3 gap-2 sm:gap-4 mt-5 pt-4 border-t border-border-subtle text-center">
          <div className="p-2.5 bg-bg-secondary rounded-xl">
            <p className="text-[11px] text-text-secondary font-medium">Not Started</p>
            <p className="text-sm font-bold text-text-primary mt-0.5">{roadmapData.not_started_items}</p>
          </div>
          <div className="p-2.5 bg-lavender/40 rounded-xl border border-lavender-text/20">
            <p className="text-[11px] text-brand font-medium">Learning</p>
            <p className="text-sm font-bold text-brand mt-0.5">{roadmapData.learning_items}</p>
          </div>
          <div className="p-2.5 bg-mint-light/50 rounded-xl border border-mint-text/20">
            <p className="text-[11px] text-mint-text font-medium">Completed</p>
            <p className="text-sm font-bold text-mint-text mt-0.5">{roadmapData.completed_items}</p>
          </div>
        </div>
      </Card>

      {/* 3. WEEKLY ROADMAP MILESTONES LIST */}
      <div className="flex flex-col gap-4">
        {roadmapData.items.map((item) => {
          const isCompleted = item.status === 'Completed';
          const isLearning = item.status === 'Learning';
          const isBusy = updatingId === item.id;

          return (
            <Card
              key={item.id}
              className={`p-5 sm:p-6 transition-all duration-200 ${
                isCompleted
                  ? 'bg-mint-light/20 border-mint-text/30'
                  : isLearning
                  ? 'bg-lavender/20 border-brand/40 shadow-soft-md'
                  : 'bg-white'
              }`}
            >
              <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-4">
                
                {/* Left: Week Badge & Details */}
                <div className="flex items-start gap-4">
                  {/* Week Indicator */}
                  <div
                    className={`w-11 h-11 rounded-2xl flex flex-col items-center justify-center font-bold flex-shrink-0 shadow-xs ${
                      isCompleted
                        ? 'bg-mint text-mint-text'
                        : isLearning
                        ? 'bg-brand text-white shadow-soft'
                        : 'bg-bg-secondary text-text-secondary border border-border-subtle'
                    }`}
                  >
                    <span className="text-[9px] uppercase tracking-tighter">Wk</span>
                    <span className="text-sm leading-none">{item.week}</span>
                  </div>

                  <div className="flex flex-col gap-1.5">
                    <div className="flex flex-wrap items-center gap-2">
                      <h3 className="text-base font-bold text-text-primary">{item.title}</h3>
                      {item.skill_name && (
                        <span className="text-xs font-semibold px-2.5 py-0.5 rounded-md bg-bg-secondary text-text-secondary border border-border-subtle">
                          {item.skill_name}
                        </span>
                      )}
                      {item.importance === 'HIGH' && (
                        <span className="text-[10px] uppercase font-bold tracking-wider px-1.5 py-0.5 rounded-md bg-amber-50 text-amber-800 border border-amber-200">
                          HIGH PRIORITY
                        </span>
                      )}
                    </div>
                    <p className="text-xs text-text-secondary leading-relaxed max-w-xl">
                      {item.description}
                    </p>
                  </div>
                </div>

                {/* Right: Status Actions Toggle Buttons */}
                <div className="flex items-center gap-1.5 self-end sm:self-center flex-shrink-0 bg-bg-secondary p-1 rounded-xl border border-border-subtle">
                  
                  <button
                    onClick={() => handleStatusChange(item.id, 'Not Started')}
                    disabled={isBusy || item.status === 'Not Started'}
                    className={`px-2.5 py-1.5 rounded-lg text-xs font-medium transition-all ${
                      item.status === 'Not Started'
                        ? 'bg-white text-text-primary shadow-xs font-semibold'
                        : 'text-text-muted hover:text-text-secondary'
                    }`}
                  >
                    Not Started
                  </button>

                  <button
                    onClick={() => handleStatusChange(item.id, 'Learning')}
                    disabled={isBusy || item.status === 'Learning'}
                    className={`px-2.5 py-1.5 rounded-lg text-xs font-medium transition-all flex items-center gap-1 ${
                      item.status === 'Learning'
                        ? 'bg-brand text-white shadow-xs font-semibold'
                        : 'text-text-muted hover:text-text-secondary'
                    }`}
                  >
                    <Clock className="w-3 h-3" />
                    Learning
                  </button>

                  <button
                    onClick={() => handleStatusChange(item.id, 'Completed')}
                    disabled={isBusy || item.status === 'Completed'}
                    className={`px-2.5 py-1.5 rounded-lg text-xs font-medium transition-all flex items-center gap-1 ${
                      item.status === 'Completed'
                        ? 'bg-status-success text-white shadow-xs font-semibold'
                        : 'text-text-muted hover:text-text-secondary'
                    }`}
                  >
                    <CheckCircle2 className="w-3 h-3" />
                    Done
                  </button>

                </div>

              </div>
            </Card>
          );
        })}
      </div>

    </div>
  );
};
