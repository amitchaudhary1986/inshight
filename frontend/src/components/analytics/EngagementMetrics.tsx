'use client';

import React, { useEffect, useState } from 'react';
import { useAuth } from '@/contexts/AuthContext';

interface EngagementData {
  interviews_started_today: number;
  interviews_completed_today: number;
  interviews_started_this_week: number;
  interviews_completed_this_week: number;
  interviews_started_this_month: number;
  interviews_completed_this_month: number;
  average_time_per_interview_minutes: number;
  interview_abandonment_rate: number;
}

export default function EngagementMetrics() {
  const { token } = useAuth();
  const [data, setData] = useState<EngagementData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchEngagementMetrics() {
      if (!token) {
        setIsLoading(false);
        setError("Authentication token not found. Please log in.");
        return;
      }

      setIsLoading(true);
      setError(null);
      const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

      try {
        const res = await fetch(`${API_URL}/api/analytics/engagement/`, {
          headers: {
            'Authorization': `Token ${token}`,
            'Content-Type': 'application/json',
          },
        });

        if (!res.ok) {
          const errorData = await res.json().catch(() => ({ detail: 'Unknown error occurred' }));
          throw new Error(errorData.detail || `Failed to fetch engagement metrics: ${res.statusText}`);
        }
        const result = await res.json();
        setData(result);
      } catch (e: any) {
        console.error('Error fetching engagement metrics:', e);
        setError(e.message || 'An unexpected error occurred.');
      } finally {
        setIsLoading(false);
      }
    }

    fetchEngagementMetrics();
  }, [token]);

  if (isLoading) {
    return <div className="p-4 bg-gray-100 rounded-lg shadow animate-pulse">Loading Engagement Metrics...</div>;
  }

  if (error) {
    return (
      <div className="p-4 bg-red-100 border border-red-400 text-red-700 rounded-lg shadow">
        <p className="font-bold">Error loading Engagement Metrics:</p>
        <p>{error}</p>
      </div>
    );
  }

  if (!data) {
    return <div className="p-4 bg-gray-100 rounded-lg shadow">No engagement data available.</div>;
  }

  const metrics = [
    { label: 'Interviews Started Today', value: data.interviews_started_today },
    { label: 'Interviews Completed Today', value: data.interviews_completed_today },
    { label: 'Interviews Started This Week', value: data.interviews_started_this_week },
    { label: 'Interviews Completed This Week', value: data.interviews_completed_this_week },
    { label: 'Interviews Started This Month', value: data.interviews_started_this_month },
    { label: 'Interviews Completed This Month', value: data.interviews_completed_this_month },
    { label: 'Avg. Interview Time (min)', value: `${data.average_time_per_interview_minutes.toFixed(2)} min` },
    { label: 'Interview Abandonment Rate', value: `${data.interview_abandonment_rate.toFixed(2)}%` },
  ];

  return (
    <div className="bg-white p-6 rounded-lg shadow-lg">
      <h2 className="text-2xl font-semibold mb-6 text-gray-800">Engagement Metrics</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {metrics.map((metric) => (
          <div key={metric.label} className="bg-indigo-50 p-4 rounded-lg shadow hover:shadow-md transition-shadow">
            <h3 className="text-sm font-medium text-indigo-600">{metric.label}</h3>
            <p className="text-3xl font-bold text-indigo-900 mt-1">{metric.value}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
