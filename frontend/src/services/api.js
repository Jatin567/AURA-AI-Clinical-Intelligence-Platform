export const API_BASE = '/api';

const getAuthHeaders = () => {
  const token = localStorage.getItem('aura_token');
  return {
    'Content-Type': 'application/json',
    ...(token && { 'Authorization': `Bearer ${token}` })
  };
};

const handleResponse = async (res) => {
  if (!res.ok) {
    if (res.status === 401) {
      localStorage.removeItem('aura_token');
      // If we're not on the login page, we might want to redirect, but for now we just throw
    }
    const errorBody = await res.json().catch(() => ({}));
    throw new Error(errorBody.detail || 'API Request Failed');
  }
  return res.json();
};

export const register = async (email, password) => {
  const res = await fetch(`${API_BASE}/auth/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password })
  });
  return handleResponse(res);
};

export const login = async (email, password) => {
  const res = await fetch(`${API_BASE}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password })
  });
  return handleResponse(res);
};

export const loginWithGoogleToken = async (idToken) => {
  const res = await fetch(`${API_BASE}/auth/google`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ token: idToken })
  });
  return handleResponse(res);
};

export const logout = async () => {
  const res = await fetch(`${API_BASE}/auth/logout`, {
    method: 'POST',
    headers: getAuthHeaders()
  });
  return handleResponse(res);
};

export const getMe = async () => {
  const res = await fetch(`${API_BASE}/patients/me`, {
    headers: getAuthHeaders()
  });
  return handleResponse(res);
};

// Returns {user_id, is_active} — always an object, used for auth state.
// /api/patients/me returns a PatientProfile list that is empty for new users,
// so AuthContext uses this endpoint instead.
export const getAuthMe = async () => {
  const res = await fetch(`${API_BASE}/auth/me`, {
    headers: getAuthHeaders()
  });
  return handleResponse(res);
};

export const getWorkspace = async (patientId, payload) => {
  const res = await fetch(`${API_BASE}/workspace/${patientId}/build`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify(payload)
  });
  return handleResponse(res);
};

export const getTimeline = async (patientId) => {
  const res = await fetch(`${API_BASE}/timeline/${patientId}`, {
    headers: getAuthHeaders()
  });
  return handleResponse(res);
};

// Existing Assessment Endpoints (Modified to use Auth Headers if needed)
export const createSession = async () => {
  const res = await fetch(`${API_BASE}/v1/session`, {
    method: 'POST',
    headers: getAuthHeaders()
  });
  return handleResponse(res);
};

export const getQuestion = async (sessionId) => {
  const res = await fetch(`${API_BASE}/v1/session/question`, {
    headers: {
      ...getAuthHeaders(),
      'X-Session-ID': sessionId
    }
  });
  return handleResponse(res);
};

export const submitAnswer = async (sessionId, questionId, answer) => {
  const res = await fetch(`${API_BASE}/v1/session/answer`, {
    method: 'POST',
    headers: {
      ...getAuthHeaders(),
      'X-Session-ID': sessionId
    },
    body: JSON.stringify({ question_id: questionId, answer })
  });
  return handleResponse(res);
};

export const getResult = async (sessionId) => {
  const res = await fetch(`${API_BASE}/v1/session/result`, {
    headers: {
      ...getAuthHeaders(),
      'X-Session-ID': sessionId
    }
  });
  return handleResponse(res);
};

// Conversation API Endpoints
export const createConversation = async (title = "New Conversation") => {
  const res = await fetch(`${API_BASE}/chat/conversations`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify({ title })
  });
  return handleResponse(res);
};

export const getConversations = async () => {
  const res = await fetch(`${API_BASE}/chat/conversations`, {
    headers: getAuthHeaders()
  });
  return handleResponse(res);
};

export const deleteConversation = async (conversationId) => {
  const res = await fetch(`${API_BASE}/chat/conversations/${conversationId}`, {
    method: 'DELETE',
    headers: getAuthHeaders()
  });
  return handleResponse(res);
};

export const renameConversation = async (conversationId, title) => {
  const res = await fetch(`${API_BASE}/chat/conversations/${conversationId}`, {
    method: 'PATCH',
    headers: getAuthHeaders(),
    body: JSON.stringify({ title })
  });
  return handleResponse(res);
};

export const getConversationMessages = async (conversationId) => {
  const res = await fetch(`${API_BASE}/chat/conversations/${conversationId}/messages`, {
    headers: getAuthHeaders()
  });
  return handleResponse(res);
};

export const transcribeSpeech = async (audioBlob) => {
  const formData = new FormData();
  formData.append('audio', audioBlob, 'audio.webm');

  const res = await fetch(`${API_BASE}/speech/transcribe`, {
    method: 'POST',
    headers: {
      ...(getAuthHeaders().Authorization ? { 'Authorization': getAuthHeaders().Authorization } : {})
    },
    body: formData
  });
  
  if (!res.ok) {
    const errorBody = await res.json().catch(() => ({}));
    throw new Error(errorBody.detail || 'Transcription failed');
  }
  return res.json();
};

export const uploadArtifact = async (conversationId, file, onProgress) => {
  const formData = new FormData();
  formData.append('file', file);
  if (conversationId) {
    formData.append('conversation_id', conversationId);
  }

  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest();
    xhr.open('POST', `${API_BASE}/artifacts/upload`);
    
    // Add auth headers
    const headers = getAuthHeaders();
    if (headers.Authorization) {
      xhr.setRequestHeader('Authorization', headers.Authorization);
    }
    // Note: Don't set Content-Type here, let the browser set it with boundary for FormData

    xhr.upload.onprogress = (event) => {
      if (event.lengthComputable && onProgress) {
        const percentComplete = Math.round((event.loaded / event.total) * 100);
        onProgress(percentComplete);
      }
    };

    xhr.onload = () => {
      if (xhr.status >= 200 && xhr.status < 300) {
        try {
          const response = JSON.parse(xhr.responseText);
          resolve(response);
        } catch {
          resolve(xhr.responseText);
        }
      } else {
        try {
          const errorResponse = JSON.parse(xhr.responseText);
          reject(new Error(errorResponse.detail || 'Upload failed'));
        } catch {
          reject(new Error('Upload failed'));
        }
      }
    };

    xhr.onerror = () => {
      reject(new Error('Network error during upload'));
    };

    xhr.send(formData);
  });
};
