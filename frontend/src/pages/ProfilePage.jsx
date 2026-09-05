import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  User as UserIcon,
  GraduationCap,
  Target,
  Mail,
  Edit3,
  FileUp,
  Sparkles,
  CheckCircle2
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../context/ToastContext';
import { Button } from '../components/Button';
import { Card } from '../components/Card';
import { SkillBadge } from '../components/SkillBadge';
import { Modal } from '../components/Modal';
import { Input } from '../components/Input';

export const ProfilePage = () => {
  const { user, updateProfile } = useAuth();
  const { showSuccess, showError } = useToast();
  const navigate = useNavigate();

  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [formData, setFormData] = useState({
    name: user?.name || '',
    education: user?.education || '',
    student_status: user?.student_status || 'B.Tech Computer Engineering Student',
  });
  const [isSaving, setIsSaving] = useState(false);

  const getInitials = (name) => {
    if (!name) return 'S';
    return name
      .split(' ')
      .map((n) => n[0])
      .join('')
      .toUpperCase()
      .substring(0, 2);
  };

  const handleOpenEdit = () => {
    setFormData({
      name: user?.name || '',
      education: user?.education || '',
      student_status: user?.student_status || 'B.Tech Computer Engineering Student',
    });
    setIsEditModalOpen(true);
  };

  const handleSaveProfile = async (e) => {
    e.preventDefault();
    setIsSaving(true);
    try {
      await updateProfile(formData);
      showSuccess('Profile updated successfully!');
      setIsEditModalOpen(false);
    } catch (err) {
      showError(err.userMessage || 'Failed to update profile.');
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto flex flex-col gap-6 py-4 animate-in fade-in duration-200">
      
      {/* 1. PROFILE HEADER CARD */}
      <Card className="p-6 sm:p-8 flex flex-col sm:flex-row items-center sm:items-start justify-between gap-6">
        <div className="flex flex-col sm:flex-row items-center gap-5 text-center sm:text-left">
          {/* Avatar with Initials */}
          <div className="w-20 h-20 rounded-3xl bg-brand text-white flex items-center justify-center font-bold text-2xl shadow-soft flex-shrink-0">
            {getInitials(user?.name)}
          </div>
          <div>
            <h1 className="text-2xl font-bold text-text-primary">{user?.name || 'Student Name'}</h1>
            <p className="text-xs font-medium text-text-secondary mt-0.5">
              {user?.student_status || 'B.Tech Computer Engineering Student'}
            </p>
            <div className="inline-flex items-center gap-1.5 mt-3 px-3 py-1 rounded-full bg-lavender text-brand text-xs font-semibold border border-lavender-text/20">
              <Target className="w-3.5 h-3.5" />
              <span>Target Career: {user?.target_career_name || 'Not Selected Yet'}</span>
            </div>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex flex-col sm:flex-row gap-2 w-full sm:w-auto">
          <Button
            variant="outline"
            size="sm"
            onClick={handleOpenEdit}
            icon={Edit3}
            className="w-full sm:w-auto"
          >
            Edit Profile
          </Button>
          <Button
            variant="primary"
            size="sm"
            onClick={() => navigate('/resume')}
            icon={FileUp}
            className="w-full sm:w-auto"
          >
            Update Resume
          </Button>
        </div>
      </Card>

      {/* 2. BASIC INFORMATION CARD */}
      <Card className="p-6">
        <h2 className="text-sm font-bold text-text-primary uppercase tracking-wider mb-4 text-text-muted">
          Basic Information
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div className="p-3.5 bg-bg-secondary rounded-xl border border-border-subtle flex items-start gap-3">
            <UserIcon className="w-4 h-4 text-text-muted mt-0.5" />
            <div>
              <p className="text-[11px] text-text-secondary font-medium">Full Name</p>
              <p className="text-xs font-semibold text-text-primary">{user?.name || '-'}</p>
            </div>
          </div>

          <div className="p-3.5 bg-bg-secondary rounded-xl border border-border-subtle flex items-start gap-3">
            <Mail className="w-4 h-4 text-text-muted mt-0.5" />
            <div>
              <p className="text-[11px] text-text-secondary font-medium">Email Address</p>
              <p className="text-xs font-semibold text-text-primary truncate max-w-[200px]">{user?.email || '-'}</p>
            </div>
          </div>

          <div className="p-3.5 bg-bg-secondary rounded-xl border border-border-subtle flex items-start gap-3 sm:col-span-2">
            <GraduationCap className="w-4 h-4 text-text-muted mt-0.5" />
            <div>
              <p className="text-[11px] text-text-secondary font-medium">Education / University</p>
              <p className="text-xs font-semibold text-text-primary">{user?.education || 'B.Tech in Computer Science'}</p>
            </div>
          </div>
        </div>
      </Card>

      {/* 3. CAREER GOAL CARD */}
      <Card className="p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-sm font-bold text-text-primary uppercase tracking-wider text-text-muted">
            Career Goal
          </h2>
          <button
            onClick={() => navigate('/career')}
            className="text-xs font-semibold text-brand hover:underline"
          >
            Change Goal
          </button>
        </div>

        <div className="p-4 bg-lavender/40 rounded-2xl border border-lavender-text/20 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-brand text-white flex items-center justify-center shadow-xs">
              <Target className="w-5 h-5" />
            </div>
            <div>
              <p className="text-xs text-text-secondary font-medium">Selected Role</p>
              <p className="text-sm font-bold text-text-primary">
                {user?.target_career_name || 'No target career selected yet'}
              </p>
            </div>
          </div>
          {!user?.target_career_id && (
            <Button variant="primary" size="sm" onClick={() => navigate('/career')}>
              Select Career
            </Button>
          )}
        </div>
      </Card>

      {/* 4. CURRENT SKILLS CARD */}
      <Card className="p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-sm font-bold text-text-primary uppercase tracking-wider text-text-muted">
            Currently Detected Skills
          </h2>
          <span className="text-xs text-text-secondary">
            {user?.skills?.length || 0} skills detected
          </span>
        </div>

        {user?.skills && user.skills.length > 0 ? (
          <div className="flex flex-wrap gap-2">
            {user.skills.map((skill) => (
              <SkillBadge key={skill} name={skill} type="neutral" />
            ))}
          </div>
        ) : (
          <div className="text-center py-6 bg-bg-secondary rounded-xl border border-border-subtle p-4">
            <Sparkles className="w-6 h-6 text-text-muted mx-auto mb-2" />
            <p className="text-xs font-semibold text-text-primary">No skills detected yet</p>
            <p className="text-[11px] text-text-secondary mt-0.5 mb-3">
              Upload your resume to extract your verified skills with Gemini AI.
            </p>
            <Button variant="primary" size="sm" onClick={() => navigate('/resume')} icon={FileUp}>
              Upload Resume
            </Button>
          </div>
        )}
      </Card>

      {/* EDIT PROFILE MODAL */}
      <Modal
        isOpen={isEditModalOpen}
        onClose={() => setIsEditModalOpen(false)}
        title="Edit Student Profile"
      >
        <form onSubmit={handleSaveProfile} className="flex flex-col gap-4">
          <Input
            label="Full Name"
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            required
          />

          <Input
            label="Student Status / Tagline"
            placeholder="e.g. B.Tech Computer Engineering Student"
            value={formData.student_status}
            onChange={(e) => setFormData({ ...formData, student_status: e.target.value })}
          />

          <Input
            label="Education / Degree"
            value={formData.education}
            onChange={(e) => setFormData({ ...formData, education: e.target.value })}
          />

          <div className="flex justify-end gap-2 pt-4 border-t border-border-subtle mt-2">
            <Button
              variant="secondary"
              size="md"
              onClick={() => setIsEditModalOpen(false)}
            >
              Cancel
            </Button>
            <Button
              type="submit"
              variant="primary"
              size="md"
              isLoading={isSaving}
            >
              Save Changes
            </Button>
          </div>
        </form>
      </Modal>

    </div>
  );
};
