import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Briefcase, ArrowRight, CheckCircle2 } from 'lucide-react';
import { careerApi } from '../services/api';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../context/ToastContext';
import { PageHeader } from '../components/PageHeader';
import { CareerCard } from '../components/CareerCard';
import { Button } from '../components/Button';
import { LoadingSpinner } from '../components/LoadingSpinner';

export const CareerPage = () => {
  const [careers, setCareers] = useState([]);
  const [selectedCareerId, setSelectedCareerId] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);

  const { user, selectCareer } = useAuth();
  const { showSuccess, showError } = useToast();
  const navigate = useNavigate();

  useEffect(() => {
    const fetchCareers = async () => {
      try {
        const response = await careerApi.getAll();
        setCareers(response.data);
        if (user?.target_career_id) {
          setSelectedCareerId(user.target_career_id);
        }
      } catch (err) {
        showError(err.userMessage || 'Failed to load career tracks.');
      } finally {
        setIsLoading(false);
      }
    };
    fetchCareers();
  }, [user?.target_career_id, showError]);

  const handleSelectCareer = (career) => {
    setSelectedCareerId(career.id);
  };

  const handleConfirm = async () => {
    if (!selectedCareerId) {
      showError('Please select a target career track.');
      return;
    }

    setIsSaving(true);
    try {
      await selectCareer(selectedCareerId);
      const chosen = careers.find((c) => c.id === selectedCareerId);
      showSuccess(`Target career updated to ${chosen?.name || 'selected role'}!`);
      // Navigate to Resume upload or Skill gap
      if (!user?.skills || user.skills.length === 0) {
        navigate('/resume');
      } else {
        navigate('/skills');
      }
    } catch (err) {
      showError(err.userMessage || 'Failed to save career choice.');
    } finally {
      setIsSaving(false);
    }
  };

  if (isLoading) {
    return <LoadingSpinner message="Loading career paths..." fullPage />;
  }

  const selectedCareer = careers.find((c) => c.id === selectedCareerId);

  return (
    <div className="flex flex-col gap-6 animate-in fade-in duration-200">
      <PageHeader
        title="Choose Your Target Career"
        subtitle="Select the technical role you are preparing for to calculate your exact skill gap."
        action={
          <Button
            variant="primary"
            size="md"
            onClick={handleConfirm}
            isLoading={isSaving}
            disabled={!selectedCareerId}
            icon={ArrowRight}
          >
            {user?.skills?.length > 0 ? 'View Skill Gap' : 'Continue to Resume'}
          </Button>
        }
      />

      {/* Career Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
        {careers.map((career) => (
          <CareerCard
            key={career.id}
            career={career}
            isSelected={selectedCareerId === career.id}
            onSelect={handleSelectCareer}
          />
        ))}
      </div>

      {/* Selected Career Summary & Action Bar */}
      {selectedCareer && (
        <div className="sticky bottom-4 z-20 bg-white/95 backdrop-blur-md rounded-2xl border border-brand/30 shadow-soft-lg p-4 flex flex-col sm:flex-row items-center justify-between gap-3 animate-in slide-in-from-bottom-3 duration-150">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-brand text-white flex items-center justify-center font-bold text-xs">
              <CheckCircle2 className="w-4 h-4" />
            </div>
            <div>
              <p className="text-xs text-text-secondary font-medium">Selected Target Role</p>
              <p className="text-sm font-bold text-text-primary">{selectedCareer.name}</p>
            </div>
          </div>
          <Button
            variant="primary"
            size="md"
            onClick={handleConfirm}
            isLoading={isSaving}
            icon={ArrowRight}
            className="w-full sm:w-auto"
          >
            Confirm & Continue
          </Button>
        </div>
      )}
    </div>
  );
};
