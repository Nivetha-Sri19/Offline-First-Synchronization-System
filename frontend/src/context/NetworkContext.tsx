import { createContext, useContext, useEffect, useMemo, useState, type ReactNode } from 'react';

const NetworkContext = createContext(true);

export function NetworkProvider({ children }: { children: ReactNode }) {
  const [online, setOnline] = useState(navigator.onLine);
  useEffect(() => {
    const on = () => setOnline(true);
    const off = () => setOnline(false);
    window.addEventListener('online', on);
    window.addEventListener('offline', off);
    return () => { window.removeEventListener('online', on); window.removeEventListener('offline', off); };
  }, []);
  return <NetworkContext.Provider value={online}>{children}</NetworkContext.Provider>;
}

export const useNetwork = () => useContext(NetworkContext);
