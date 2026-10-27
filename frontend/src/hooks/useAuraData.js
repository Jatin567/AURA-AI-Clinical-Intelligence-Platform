import { useQuery } from '@tanstack/react-query';
import { apiClient } from '../api/apiClient';

/**
 * Fetch patient timeline data
 */
export function usePatientTimeline(patientId) {
  return useQuery({
    queryKey: ['timeline', patientId],
    queryFn: () => apiClient(`/timeline/${patientId}`),
    enabled: !!patientId,
  });
}

/**
 * Fetch the current user's patient profiles
 */
export function usePatientProfiles() {
  return useQuery({
    queryKey: ['profiles', 'me'],
    queryFn: () => apiClient('/patients/me'),
  });
}

/**
 * Fetch the workspace aggregation
 * Note: The backend requires current_report and current_explanation in the payload for now.
 * We can pass dummy data or handle this gracefully.
 */
export function useWorkspaceData(patientId, reportData, explanationData) {
  const hasData = Boolean(
    reportData && Object.keys(reportData).length > 0 && 
    explanationData && Object.keys(explanationData).length > 0
  );

  return useQuery({
    queryKey: ['workspace', patientId, reportData, explanationData],
    queryFn: () => apiClient(`/workspace/${patientId}/build`, {
      data: {
        current_report: reportData,
        current_explanation: explanationData
      }
    }),
    enabled: !!patientId && hasData,
    retry: false, // Don't retry if the payload was rejected
  });
}
