import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
});

// Request interceptor to attach JWT auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('skillgap_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor to format clean human-readable errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    let message = 'An unexpected error occurred. Please try again.';
    if (error.response) {
      if (error.response.data && error.response.data.detail) {
        message = error.response.data.detail;
      } else if (error.response.status === 401) {
        message = 'Your session has expired. Please log in again.';
        localStorage.removeItem('skillgap_token');
        localStorage.removeItem('skillgap_user');
      } else if (error.response.status === 404) {
        message = 'Requested resource was not found.';
      } else if (error.response.status >= 500) {
        message = 'Server is currently experiencing issues. Please try again shortly.';
      }
    } else if (error.request) {
      message = 'Unable to reach the server. Please check your internet connection.';
    }
    error.userMessage = message;
    return Promise.reject(error);
  }
);

// Centralized API modules
export const authApi = {
  register: (data) => api.post('/auth/register', data),
  login: (data) => api.post('/auth/login', data),
};

export const userApi = {
  getProfile: () => api.get('/users/me'),
  updateProfile: (data) => api.put('/users/me', data),
  selectTargetCareer: (career_id) => api.post('/users/target-career', { career_id }),
};

export const careerApi = {
  getAll: () => api.get('/careers'),
  getById: (id) => api.get(`/careers/${id}`),
};

export const resumeApi = {
  analyzeResume: (formData) =>
    api.post('/resumes/analyze', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      timeout: 60000, // Gemini AI processing may take up to a minute
    }),
};

export const skillApi = {
  getSkillGap: () => api.get('/skills/gap'),
  getUserSkills: () => api.get('/skills/user'),
};

export const dashboardApi = {
  getDashboardData: () => api.get('/dashboard'),
};

export const roadmapApi = {
  getRoadmap: () => api.get('/roadmap'),
  updateItemStatus: (id, status) => api.put(`/roadmap/${id}`, { status }),
};

export default api;
