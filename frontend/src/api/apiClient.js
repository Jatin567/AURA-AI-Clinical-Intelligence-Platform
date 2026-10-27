const API_BASE_URL = 'http://localhost:8000/api'; // Or from import.meta.env

/**
 * Custom error class for API errors
 */
export class ApiError extends Error {
  constructor(message, status, data) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.data = data;
  }
}

/**
 * Base fetch wrapper that handles JSON parsing and error checking
 */
export async function apiClient(endpoint, { data, ...customConfig } = {}) {
  // Get token if auth is implemented
  const token = localStorage.getItem('aura_token'); // Or however auth is stored
  
  const headers = {
    'Content-Type': 'application/json',
  };

  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  const config = {
    method: data ? 'POST' : 'GET',
    ...customConfig,
    headers: {
      ...headers,
      ...customConfig.headers,
    },
  };

  if (data) {
    config.body = JSON.stringify(data);
  }

  const response = await fetch(`${API_BASE_URL}${endpoint}`, config);
  
  if (!response.ok) {
    let errorData = null;
    try {
      errorData = await response.json();
    } catch {
      // Not JSON
    }

    // Mask Pydantic validation errors
    if (response.status === 422) {
      throw new ApiError(
        'The provided data was incomplete or invalid. Please review and try again.',
        422,
        { masked: true }
      );
    }

    throw new ApiError(
      errorData?.detail || response.statusText || 'An error occurred',
      response.status,
      errorData
    );
  }

  if (response.status === 204) {
    return null; // No content
  }

  return response.json();
}
