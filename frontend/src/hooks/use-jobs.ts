import { useState, useEffect, useCallback } from 'react';
import type { Job } from '@/data/sample-jobs';
import { api } from '@/lib/api';

function sortJobs(jobs: Job[]): Job[] {
  return [...jobs].sort((a, b) => {
    // First, sort by applied status (NO first, others last)
    if (a.applied === 'NO' && b.applied !== 'NO') return -1;
    if (a.applied !== 'NO' && b.applied === 'NO') return 1;

    // If both have the same applied status, sort by timestamp (most recent first)
    const timestampA = parseFloat(a.timeStamp);
    const timestampB = parseFloat(b.timeStamp);
    return timestampB - timestampA;
  });
}

export function useJobs() {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchJobs = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);
      const data = await api.getJobs();
      const sortedJobs = sortJobs(data);
      setJobs(sortedJobs);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch jobs');
      console.error('Error fetching jobs:', err);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const updateJobStatus = useCallback((jobId: string, newStatus: 'YES' | 'NEVER') => {
    setJobs(prevJobs => {
      const updatedJobs = prevJobs.map(job => 
        job.id === jobId ? { ...job, applied: newStatus } : job
      );
      return sortJobs(updatedJobs);
    });
  }, []);

  useEffect(() => {
    fetchJobs();
  }, [fetchJobs]);

  return { jobs, isLoading, error, updateJobStatus };
}