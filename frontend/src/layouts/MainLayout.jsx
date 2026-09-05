import React from 'react';
import { Outlet } from 'react-router-dom';
import { Navbar } from '../components/Navbar';

export const MainLayout = () => {
  return (
    <div className="min-h-screen flex flex-col bg-background selection:bg-brand-light selection:text-brand">
      <Navbar />
      <main className="flex-1 w-full max-w-[1200px] mx-auto px-4 sm:px-6 py-6 sm:py-8">
        <Outlet />
      </main>
      <footer className="border-t border-border-subtle bg-white/50 py-6 mt-12">
        <div className="max-w-[1200px] mx-auto px-4 sm:px-6 flex flex-col sm:flex-row items-center justify-between gap-3 text-xs text-text-secondary">
          <p>© 2026 SkillGap AI — Student Skill Gap Analyzer (Phase 1)</p>
          <div className="flex items-center gap-4">
            <span>Powered by Gemini AI</span>
            <span>•</span>
            <span>Deterministic Scoring</span>
            <span>•</span>
            <span>Local SQLite</span>
          </div>
        </div>
      </footer>
    </div>
  );
};
