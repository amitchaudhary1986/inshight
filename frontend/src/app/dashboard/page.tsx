'use client';

import React, { useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { useRouter } from 'next/navigation';
import EngagementMetrics from '@/components/analytics/EngagementMetrics';
import CandidateProgression from '@/components/analytics/CandidateProgression';

export default function DashboardPage() {
  const { isAuthenticated, isLoading: authLoading, user } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push('/login');
    }
  }, [authLoading, isAuthenticated, router]);

  if (authLoading || (!isAuthenticated && !authLoading)) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <p className="text-lg text-gray-700">Loading dashboard...</p>
      </div>
    );
  }
  
  // Ensure this part only renders if authenticated
  if (!isAuthenticated) {
    // This should ideally not be reached if redirection works correctly,
    // but serves as a fallback.
     return (
        <div className="flex justify-center items-center min-h-screen">
            <p className="text-lg text-red-500">Access Denied. Redirecting to login...</p>
        </div>
    );
  }

  return (
    <div className="container mx-auto p-4 space-y-8">
      <div>
        <h1 className="text-3xl font-bold mb-2 text-gray-800">Analytics Dashboard</h1>
        <p className="text-lg text-gray-600">Welcome, {user?.username || 'User'}! Here&apos;s an overview of your platform activity.</p>
      </div>
      
      {/* Render Engagement Metrics */}
      <EngagementMetrics />
      
      {/* Render Candidate Progression */}
      <CandidateProgression />

      {/* 
        The previous employer list has been removed as per the task to focus on analytics.
        If needed, it can be added back as a separate component or on a different page.
      */}
    </div>
  );
}
