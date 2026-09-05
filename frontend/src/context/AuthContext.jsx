import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { authApi, userApi } from '../services/api';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(() => {
    const saved = localStorage.getItem('skillgap_user');
    return saved ? JSON.parse(saved) : null;
  });
  const [token, setToken] = useState(() => localStorage.getItem('skillgap_token'));
  const [isLoading, setIsLoading] = useState(true);

  // Fetch fresh profile on mount if token exists
  const fetchCurrentUser = useCallback(async () => {
    const savedToken = localStorage.getItem('skillgap_token');
    if (!savedToken) {
      setUser(null);
      setIsLoading(false);
      return;
    }

    try {
      const response = await userApi.getProfile();
      setUser(response.data);
      localStorage.setItem('skillgap_user', JSON.stringify(response.data));
    } catch (err) {
      console.warn('Failed to load profile from token:', err);
      // If 401, token is removed by interceptor
      setUser(null);
      setToken(null);
      localStorage.removeItem('skillgap_token');
      localStorage.removeItem('skillgap_user');
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchCurrentUser();
  }, [fetchCurrentUser]);

  const login = async (email, password) => {
    const response = await authApi.login({ email, password });
    const { access_token, user: userData } = response.data;
    localStorage.setItem('skillgap_token', access_token);
    localStorage.setItem('skillgap_user', JSON.stringify(userData));
    setToken(access_token);
    setUser(userData);
    // Also fetch complete profile with skills
    await fetchCurrentUser();
    return userData;
  };

  const register = async (formData) => {
    const response = await authApi.register(formData);
    const { access_token, user: userData } = response.data;
    localStorage.setItem('skillgap_token', access_token);
    localStorage.setItem('skillgap_user', JSON.stringify(userData));
    setToken(access_token);
    setUser(userData);
    await fetchCurrentUser();
    return userData;
  };

  const logout = () => {
    localStorage.removeItem('skillgap_token');
    localStorage.removeItem('skillgap_user');
    setToken(null);
    setUser(null);
  };

  const updateProfile = async (data) => {
    const response = await userApi.updateProfile(data);
    setUser(response.data);
    localStorage.setItem('skillgap_user', JSON.stringify(response.data));
    return response.data;
  };

  const selectCareer = async (careerId) => {
    const response = await userApi.selectTargetCareer(careerId);
    setUser(response.data);
    localStorage.setItem('skillgap_user', JSON.stringify(response.data));
    return response.data;
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        isAuthenticated: !!token && !!user,
        isLoading,
        login,
        register,
        logout,
        refreshUser: fetchCurrentUser,
        updateProfile,
        selectCareer,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
