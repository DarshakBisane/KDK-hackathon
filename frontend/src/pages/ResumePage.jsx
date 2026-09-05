import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { FileText, Sparkles, ArrowRight, CheckCircle2, AlertCircle } from 'lucide-react';
import { resumeApi } from '../services/api';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../context/ToastContext';
import { PageHeader } from '../components/PageHeader';
import { FileUpload } from '../components/FileUpload';
import { Card } from '../components/Card';
import { SkillBadge } from '../components/SkillBadge';
import { Button } from '../components/Button';

export const ResumePage = () => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [processingStep, setProcessingStep] = useState('');
  const [extractedResult, setExtractedResult] = useState(null);

  const { user, refreshUser } = useAuth();
  const { showSuccess, showError } = useToast();
  const navigate = useNavigate();

  const handleFileSelect = (file) => {
    if (!file.name.toLowerCase().endsWith('.pdf')) {
      showError('Please upload a PDF file.');
      return;
    }
    if (file.size > 10 * 1024 * 1024) {
      showError('File size exceeds the 10MB limit.');
      return;
    }
    setSelectedFile(file);
    setExtractedResult(null);
  };

  const handleAnalyze = async () => {
    if (!selectedFile) {
      showError('Please select a PDF resume first.');
      return;
    }

    setIsProcessing(true);
    setProcessingStep('Uploading');

    // Simulate UX transitions between backend stages
    const stepTimer1 = setTimeout(() => setProcessingStep('Extracting Resume Text'), 800);
    const stepTimer2 = setTimeout(() => setProcessingStep('Analyzing Skills with Gemini AI'), 1800);
    const stepTimer3 = setTimeout(() => setProcessingStep('Calculating Skill Gap & Normalizing'), 3200);

    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      const response = await resumeApi.analyzeResume(formData);
      clearTimeout(stepTimer1);
      clearTimeout(stepTimer2);
      clearTimeout(stepTimer3);
      setProcessingStep('Complete');

      setExtractedResult(response.data);
      await refreshUser();
      showSuccess('Resume successfully analyzed with Gemini AI!');
    } catch (err) {
      clearTimeout(stepTimer1);
      clearTimeout(stepTimer2);
      clearTimeout(stepTimer3);
      showError(err.userMessage || 'Failed to analyze resume. Please try again.');
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto flex flex-col gap-6 animate-in fade-in duration-200">
      <PageHeader
        title="Upload Your Resume"
        subtitle="Our backend extracts your resume text and uses Gemini AI to detect your verified skillset."
      />

      {/* Target Career Status Banner */}
      {!user?.target_career_id && (
        <div className="p-4 bg-amber-50 rounded-2xl border border-amber-200/80 flex items-center justify-between gap-3 text-xs text-amber-900">
          <div className="flex items-center gap-2.5">
            <AlertCircle className="w-4 h-4 text-status-warning flex-shrink-0" />
            <span>You haven't chosen a target career yet. Choose one to compute your skill gap.</span>
          </div>
          <Button
            variant="outline"
            size="sm"
            onClick={() => navigate('/career')}
            className="flex-shrink-0 bg-white"
          >
            Select Career
          </Button>
        </div>
      )}

      {/* File Upload Dropzone */}
      <FileUpload
        selectedFile={selectedFile}
        onFileSelect={handleFileSelect}
        onRemoveFile={() => {
          setSelectedFile(null);
          setExtractedResult(null);
        }}
        onAnalyze={handleAnalyze}
        isProcessing={isProcessing}
        processingStep={processingStep}
      />

      {/* Extracted Skills Result */}
      {extractedResult && (
        <Card className="p-6 sm:p-8 animate-in fade-in slide-in-from-bottom-2 duration-300">
          <div className="flex items-center justify-between pb-4 border-b border-border-subtle mb-4">
            <div className="flex items-center gap-2.5">
              <div className="w-8 h-8 rounded-lg bg-mint text-mint-text flex items-center justify-center">
                <CheckCircle2 className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-sm font-bold text-text-primary">Skills Extracted Successfully</h3>
                <p className="text-xs text-text-secondary">
                  Detected {extractedResult.extracted_skills_count} skills from your resume
                </p>
              </div>
            </div>
            {extractedResult.readiness_score !== null && (
              <span className="text-xs font-semibold px-3 py-1 rounded-full bg-mint text-mint-text border border-mint-text/20">
                {extractedResult.readiness_score}% Match
              </span>
            )}
          </div>

          <div className="flex flex-wrap gap-2 mb-6">
            {extractedResult.extracted_skills.map((skill) => (
              <SkillBadge key={skill} name={skill} type="matched" />
            ))}
          </div>

          <div className="flex flex-col sm:flex-row items-center justify-between gap-3 pt-4 border-t border-border-subtle bg-bg-secondary/40 -mx-6 -mb-6 p-6 rounded-b-2xl">
            <span className="text-xs text-text-secondary">
              Target: <strong className="text-text-primary">{user?.target_career_name || 'Not set'}</strong>
            </span>
            <Button
              variant="primary"
              size="md"
              onClick={() => navigate('/skills')}
              icon={ArrowRight}
            >
              View Full Skill Gap
            </Button>
          </div>
        </Card>
      )}

      {/* Existing Detected Skills if user has prior extractions */}
      {!extractedResult && user?.skills && user.skills.length > 0 && (
        <Card className="p-6">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-xs font-bold text-text-muted uppercase tracking-wider">
              Currently Registered Skills ({user.skills.length})
            </h3>
            <button
              onClick={() => navigate('/skills')}
              className="text-xs font-semibold text-brand hover:underline"
            >
              View Gap Analysis →
            </button>
          </div>
          <div className="flex flex-wrap gap-2">
            {user.skills.map((s) => (
              <SkillBadge key={s} name={s} type="neutral" />
            ))}
          </div>
        </Card>
      )}

    </div>
  );
};
