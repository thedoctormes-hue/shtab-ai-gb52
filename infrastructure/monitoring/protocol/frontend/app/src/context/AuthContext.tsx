import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import * as authAPI from '../api/auth';

interface AuthContextType {
  user: { token: string; tg_id?: string } | null;
  login: (tg_id: string) => Promise<void>;
  logout: () => void;
  loading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<{ token: string; tg_id?: string } | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('jwt_token');
    if (token) {
      setUser({ token });
    }
    setLoading(false);
  }, []);

  const login = useCallback(async (tg_id: string) => {
    const res = await authAPI.login(tg_id);
    const { access_token, user_id } = res.data;
    localStorage.setItem('jwt_token', access_token);
    localStorage.setItem('user_id', user_id);
    setUser({ token: access_token, tg_id, user_id });
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem('jwt_token');
    setUser(null);
    window.location.href = '/login';
  }, []);

  return (
    <AuthContext.Provider value={{ user, login, logout, loading }}>
      {!loading && children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used within AuthProvider');
  return context;
};
