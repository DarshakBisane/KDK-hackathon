import React from 'react';
import { Link } from 'react-router-dom';
import {
  ArrowRight,
  Sparkles,
  UserCheck,
  FileUp,
  Target,
  Compass,
  CheckCircle2,
  TrendingUp,
  ShieldCheck,
  Cpu
} from 'lucide-react';
import { Button } from '../components/Button';
import { Card } from '../components/Card';

export const LandingPage = () => {
  return (
    <div className="flex flex-col gap-16 sm:gap-24 py-4 sm:py-8">
      
      {/* 1. HERO SECTION */}
      <section className="flex flex-col items-center text-center max-w-3xl mx-auto pt-6 sm:pt-12">
        <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-lavender text-brand border border-lavender-text/20 text-xs font-semibold mb-6 shadow-xs animate-in fade-in duration-300">
          <Sparkles className="w-3.5 h-3.5" />
          <span>AI-Powered Career Intelligence for Students</span>
        </div>

        <h1 className="text-3xl sm:text-5xl font-extrabold tracking-tight text-text-primary leading-[1.15] mb-5">
          Know Your Skill Gap. <br />
          <span className="text-brand">Build Your Career.</span>
        </h1>

        <p className="text-base sm:text-lg text-text-secondary leading-relaxed max-w-2xl mb-8">
          Analyze your current skills from your resume, compare them with your target career role, and get a personalized learning roadmap powered by Gemini AI.
        </p>

        <div className="flex flex-col sm:flex-row items-center gap-3 w-full sm:w-auto">
          <Link to="/register" className="w-full sm:w-auto">
            <Button variant="primary" size="lg" className="w-full sm:w-auto" icon={ArrowRight}>
              Get Started Free
            </Button>
          </Link>
          <a href="#how-it-works" className="w-full sm:w-auto">
            <Button variant="outline" size="lg" className="w-full sm:w-auto">
              See How It Works
            </Button>
          </a>
        </div>

        {/* Hero Visual Pipeline: Student Profile -> Skills -> Career -> Skill Gap -> Roadmap */}
        <div className="mt-12 sm:mt-16 w-full p-6 sm:p-8 bg-white rounded-3xl border border-border-subtle shadow-soft-lg">
          <p className="text-xs font-semibold text-text-muted uppercase tracking-wider mb-6">
            The Phase 1 Skill Gap Pipeline
          </p>
          <div className="grid grid-cols-2 sm:grid-cols-5 gap-3 items-center">
            
            <div className="p-4 bg-bg-secondary rounded-2xl border border-border-subtle flex flex-col items-center gap-2">
              <div className="w-9 h-9 rounded-xl bg-white text-brand flex items-center justify-center shadow-xs">
                <UserCheck className="w-4 h-4" />
              </div>
              <span className="text-xs font-semibold text-text-primary">1. Profile</span>
            </div>

            <div className="hidden sm:flex justify-center text-text-muted">
              <ArrowRight className="w-4 h-4" />
            </div>

            <div className="p-4 bg-paleblue-light rounded-2xl border border-paleblue-text/20 flex flex-col items-center gap-2">
              <div className="w-9 h-9 rounded-xl bg-white text-paleblue-text flex items-center justify-center shadow-xs">
                <FileUp className="w-4 h-4" />
              </div>
              <span className="text-xs font-semibold text-text-primary">2. Resume AI</span>
            </div>

            <div className="hidden sm:flex justify-center text-text-muted">
              <ArrowRight className="w-4 h-4" />
            </div>

            <div className="p-4 bg-mint-light rounded-2xl border border-mint-text/20 flex flex-col items-center gap-2 col-span-2 sm:col-span-1">
              <div className="w-9 h-9 rounded-xl bg-white text-mint-text flex items-center justify-center shadow-xs">
                <Compass className="w-4 h-4" />
              </div>
              <span className="text-xs font-semibold text-text-primary">3. Roadmap</span>
            </div>

          </div>
        </div>
      </section>

      {/* 2. HOW IT WORKS SECTION */}
      <section id="how-it-works" className="max-w-4xl mx-auto w-full scroll-mt-24">
        <div className="text-center mb-12">
          <span className="text-xs font-semibold text-brand uppercase tracking-wider">
            Simple 4-Step Process
          </span>
          <h2 className="text-2xl sm:text-3xl font-bold text-text-primary mt-1.5">
            How SkillGap AI Works
          </h2>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
          <Card className="flex flex-col gap-3">
            <div className="w-10 h-10 rounded-xl bg-lavender text-brand font-bold flex items-center justify-center text-sm">
              01
            </div>
            <h3 className="text-base font-semibold text-text-primary">Create Your Student Profile</h3>
            <p className="text-xs text-text-secondary leading-relaxed">
              Sign up in seconds and specify your educational background and target technology roles.
            </p>
          </Card>

          <Card className="flex flex-col gap-3">
            <div className="w-10 h-10 rounded-xl bg-paleblue-light text-paleblue-text font-bold flex items-center justify-center text-sm">
              02
            </div>
            <h3 className="text-base font-semibold text-text-primary">Upload Your Resume</h3>
            <p className="text-xs text-text-secondary leading-relaxed">
              Upload your text PDF. Gemini AI parses projects and coursework to extract verified technical skills.
            </p>
          </Card>

          <Card className="flex flex-col gap-3">
            <div className="w-10 h-10 rounded-xl bg-amber-50 text-amber-800 font-bold flex items-center justify-center text-sm">
              03
            </div>
            <h3 className="text-base font-semibold text-text-primary">Analyze Deterministic Gap</h3>
            <p className="text-xs text-text-secondary leading-relaxed">
              Our deterministic backend engine computes your exact readiness score against industry-seeded roles.
            </p>
          </Card>

          <Card className="flex flex-col gap-3">
            <div className="w-10 h-10 rounded-xl bg-mint-light text-mint-text font-bold flex items-center justify-center text-sm">
              04
            </div>
            <h3 className="text-base font-semibold text-text-primary">Follow Your Roadmap</h3>
            <p className="text-xs text-text-secondary leading-relaxed">
              Track your weekly milestones from Not Started to Learning and Completed to systematically bridge gaps.
            </p>
          </Card>
        </div>
      </section>

      {/* 3. WHY USE IT SECTION */}
      <section className="max-w-4xl mx-auto w-full">
        <div className="text-center mb-12">
          <span className="text-xs font-semibold text-brand uppercase tracking-wider">
            Key Advantages
          </span>
          <h2 className="text-2xl sm:text-3xl font-bold text-text-primary mt-1.5">
            Why Students Rely On SkillGap AI
          </h2>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-5">
          <Card className="flex flex-col items-center text-center p-6">
            <div className="w-12 h-12 rounded-2xl bg-lavender text-brand flex items-center justify-center mb-4">
              <Target className="w-6 h-6" />
            </div>
            <h3 className="text-sm font-semibold text-text-primary mb-2">Find Missing Skills</h3>
            <p className="text-xs text-text-secondary leading-relaxed">
              Never guess what you need to study. Pinpoint high-priority skills needed for roles like ML Engineer or Cloud Architect.
            </p>
          </Card>

          <Card className="flex flex-col items-center text-center p-6">
            <div className="w-12 h-12 rounded-2xl bg-mint-light text-mint-text flex items-center justify-center mb-4">
              <TrendingUp className="w-6 h-6" />
            </div>
            <h3 className="text-sm font-semibold text-text-primary mb-2">Understand Career Readiness</h3>
            <p className="text-xs text-text-secondary leading-relaxed">
              Get an objective, reproducible readiness score calculated directly from matched requirements.
            </p>
          </Card>

          <Card className="flex flex-col items-center text-center p-6">
            <div className="w-12 h-12 rounded-2xl bg-paleblue-light text-paleblue-text flex items-center justify-center mb-4">
              <Compass className="w-6 h-6" />
            </div>
            <h3 className="text-sm font-semibold text-text-primary mb-2">Personalized Roadmap</h3>
            <p className="text-xs text-text-secondary leading-relaxed">
              Turn abstract skill gaps into practical, week-by-week learning milestones you can update anytime.
            </p>
          </Card>
        </div>
      </section>

      {/* 4. CTA BANNER */}
      <section className="max-w-3xl mx-auto w-full">
        <div className="bg-lavender rounded-3xl p-8 sm:p-12 text-center border border-lavender-text/20 shadow-soft-md flex flex-col items-center">
          <h2 className="text-2xl sm:text-3xl font-extrabold text-text-primary mb-3">
            Start Your Career Analysis Today
          </h2>
          <p className="text-xs sm:text-sm text-text-secondary max-w-lg mb-6 leading-relaxed">
            Join students using Gemini AI to discover their exact skill gaps and accelerate their career preparation.
          </p>
          <Link to="/register">
            <Button variant="primary" size="lg" icon={ArrowRight}>
              Create Student Account
            </Button>
          </Link>
        </div>
      </section>

    </div>
  );
};
