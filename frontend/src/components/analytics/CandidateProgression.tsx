'use client';

import React, { useEffect, useState } from 'react';
import { useAuth } from '@/contexts/AuthContext';

interface StageData {
  count: number;
  display_name: string;
  drop_off_from_previous_stage_percentage?: number;
}

interface CandidateProgressionData {
  [key: string]: StageData; // e.g., "Invited", "Started", etc.
}

// Define a sensible order for stages in the funnel
const FUNNEL_STAGE_ORDER: (keyof InterviewStatusChoices)[] = [
  'Invited',
  'Started',
  'Completed',
  'Shortlisted',
  'Selected',
];

// Match Interview.STATUS_CHOICES defined in Django models
// This helps in maintaining consistency if new stages are added or order changes.
// However, for a strict funnel, the order above (FUNNEL_STAGE_ORDER) is king.
type InterviewStatusChoices = {
  Invited: string;
  Started: string;
  Completed: string;
  Shortlisted: string;
  Selected: string;
};


export default function CandidateProgression() {
  const { token } = useAuth();
  const [data, setData] = useState<CandidateProgressionData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchCandidateProgression() {
      if (!token) {
        setIsLoading(false);
        setError("Authentication token not found. Please log in.");
        return;
      }

      setIsLoading(true);
      setError(null);
      const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

      try {
        const res = await fetch(`${API_URL}/api/analytics/candidate-progression/`, {
          headers: {
            'Authorization': `Token ${token}`,
            'Content-Type': 'application/json',
          },
        });

        if (!res.ok) {
          const errorData = await res.json().catch(() => ({ detail: 'Unknown error occurred' }));
          throw new Error(errorData.detail || `Failed to fetch candidate progression data: ${res.statusText}`);
        }
        const result = await res.json();
        setData(result);
      } catch (e: any) {
        console.error('Error fetching candidate progression data:', e);
        setError(e.message || 'An unexpected error occurred.');
      } finally {
        setIsLoading(false);
      }
    }

    fetchCandidateProgression();
  }, [token]);

  if (isLoading) {
    return <div className="p-4 bg-gray-100 rounded-lg shadow animate-pulse">Loading Candidate Progression...</div>;
  }

  if (error) {
    return (
      <div className="p-4 bg-red-100 border border-red-400 text-red-700 rounded-lg shadow">
        <p className="font-bold">Error loading Candidate Progression:</p>
        <p>{error}</p>
      </div>
    );
  }

  if (!data || Object.keys(data).length === 0) {
    return <div className="p-4 bg-gray-100 rounded-lg shadow">No candidate progression data available.</div>;
  }

  // Calculate max count for funnel bar width scaling
  const maxCount = Math.max(...FUNNEL_STAGE_ORDER.map(stageKey => data[stageKey]?.count || 0), 0);


  return (
    <div className="bg-white p-6 rounded-lg shadow-lg mt-8">
      <h2 className="text-2xl font-semibold mb-6 text-gray-800">Candidate Progression Funnel</h2>
      <div className="space-y-4">
        {FUNNEL_STAGE_ORDER.map((stageKey, index) => {
          const stage = data[stageKey];
          if (!stage) return null; // Should not happen if backend sends all stages

          const barWidth = maxCount > 0 ? (stage.count / maxCount) * 100 : 0;

          return (
            <div key={stageKey} className="p-4 border rounded-lg shadow-sm bg-gray-50 hover:shadow-md transition-shadow">
              <div className="flex justify-between items-center mb-2">
                <h3 className="text-lg font-medium text-purple-700">{stage.display_name}</h3>
                <span className="text-2xl font-bold text-purple-900">{stage.count}</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-6 dark:bg-gray-700">
                <div
                  className="bg-purple-600 h-6 rounded-full transition-all duration-500 ease-out"
                  style={{ width: `${barWidth}%` }}
                  title={`Count: ${stage.count}`}
                ></div>
              </div>
              {index > 0 && stage.drop_off_from_previous_stage_percentage !== undefined && (
                 <p className="text-xs text-red-500 mt-1 text-right">
                   Drop-off from {data[FUNNEL_STAGE_ORDER[index-1]]?.display_name || 'previous'}: {stage.drop_off_from_previous_stage_percentage.toFixed(1)}%
                 </p>
              )}
               {index === 0 && stage.drop_off_from_previous_stage_percentage !== undefined && (
                 <p className="text-xs text-gray-500 mt-1 text-right">
                   Initial stage
                 </p>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
