'use client';

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { useRouter } from 'next/navigation';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface User {
  pk: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
}

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (data: any) => Promise<void>;
  logout: () => Promise<void>;
  register: (data: any) => Promise<void>;
  error: string | null;
  clearError: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [token, setToken] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  useEffect(() => {
    const storedToken = localStorage.getItem('authToken');
    if (storedToken) {
      setToken(storedToken);
      fetchUserDetails(storedToken);
    } else {
      setIsLoading(false);
    }
  }, []);

  const fetchUserDetails = async (currentToken: string) => {
    setIsLoading(true);
    try {
      const res = await fetch(`${API_URL}/api/auth/user/`, {
        headers: {
          'Authorization': `Token ${currentToken}`,
          'Content-Type': 'application/json',
        },
      });
      if (res.ok) {
        const userData = await res.json();
        setUser(userData);
        setIsAuthenticated(true);
      } else {
        // Token might be invalid or expired
        localStorage.removeItem('authToken');
        setToken(null);
        setUser(null);
        setIsAuthenticated(false);
        if (res.status === 401) {
          // Don't set an error for auth failures on load, just ensure user is logged out
          console.warn('Token validation failed, user logged out.');
        } else {
          setError('Failed to fetch user details.');
        }
      }
    } catch (e) {
      setError('An error occurred while fetching user details.');
      console.error(e);
      localStorage.removeItem('authToken'); // Clear token on error too
      setToken(null);
      setUser(null);
      setIsAuthenticated(false);
    } finally {
      setIsLoading(false);
    }
  };

  const login = async (data: any) => {
    setIsLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API_URL}/api/auth/login/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      });
      const responseData = await res.json();
      if (res.ok && responseData.key) {
        localStorage.setItem('authToken', responseData.key);
        setToken(responseData.key);
        await fetchUserDetails(responseData.key); // Fetch user details after login
        router.push('/dashboard');
      } else {
        const errorMsg = responseData.non_field_errors?.[0] || 
                         responseData.detail || 
                         'Login failed. Please check your credentials.';
        setError(errorMsg);
        setIsAuthenticated(false);
      }
    } catch (e) {
      setError('An error occurred during login.');
      console.error(e);
      setIsAuthenticated(false);
    } finally {
      setIsLoading(false);
    }
  };

  const register = async (data: any) => {
    setIsLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API_URL}/api/auth/registration/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      });
      const responseData = await res.json();
      if (res.status === 201) { // 201 Created for successful registration
        // Optionally, log the user in directly or redirect to login
        // For now, redirect to login page with a success message (or handle globally)
        router.push('/login?registered=true');
      } else {
        // Handle errors (e.g., email already exists, password too short)
        let errorMessages = [];
        for (const key in responseData) {
          if (Array.isArray(responseData[key])) {
            errorMessages.push(`${key}: ${responseData[key].join(' ')}`);
          }
        }
        setError(errorMessages.length > 0 ? errorMessages.join('; ') : 'Registration failed.');
      }
    } catch (e) {
      setError('An error occurred during registration.');
      console.error(e);
    } finally {
      setIsLoading(false);
    }
  };

  const logout = async () => {
    setIsLoading(true);
    setError(null);
    try {
      if (token) {
        await fetch(`${API_URL}/api/auth/logout/`, {
          method: 'POST',
          headers: {
            'Authorization': `Token ${token}`,
            'Content-Type': 'application/json',
          },
        });
      }
    } catch (e) {
      // Log error but proceed with local logout
      console.error('Error during server logout:', e);
    } finally {
      localStorage.removeItem('authToken');
      setToken(null);
      setUser(null);
      setIsAuthenticated(false);
      setIsLoading(false);
      router.push('/login');
    }
  };
  
  const clearError = () => {
    setError(null);
  };

  return (
    <AuthContext.Provider value={{ user, isAuthenticated, isLoading, login, logout, register, error, clearError }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
