import { createContext, useContext, useEffect, useMemo, useState, type ReactNode } from 'react';
import { authApi } from '../api/services';
import type { User } from '../types';

interface AuthContextValue {
  user: User | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, full_name: string) => Promise<void>;
  logout: () => void;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(() => {
    const cached = localStorage.getItem('sync_user');
    return cached ? JSON.parse(cached) : null;
  });
  const [loading, setLoading] = useState(Boolean(localStorage.getItem('access_token')));

  const refreshUser = async () => {
    if (!localStorage.getItem('access_token')) { setLoading(false); return; }
    try {
      const { data } = await authApi.me();
      setUser(data);
      localStorage.setItem('sync_user', JSON.stringify(data));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { void refreshUser(); }, []);

  const login = async (email: string, password: string) => {
    const { data } = await authApi.login({ email, password });
    localStorage.setItem('access_token', data.access_token);
    localStorage.setItem('refresh_token', data.refresh_token);
    await refreshUser();
  };

  const register = async (email: string, password: string, full_name: string) => {
    await authApi.register({ email, password, full_name });
    await login(email, password);
  };

  const logout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('sync_user');
    setUser(null);
  };

  const value = useMemo(() => ({ user, loading, login, register, logout, refreshUser }), [user, loading]);
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export const useAuth = () => {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used inside AuthProvider');
  return ctx;
};
