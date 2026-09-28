import { createContext, useCallback, useContext, useEffect, useMemo, useState, type ReactNode } from 'react';
import { syncApi } from '../api/services';
import { localDb } from '../db/localDb';
import { useNetwork } from './NetworkContext';
import type { SyncPushResponse } from '../types';

interface SyncContextValue {
  pendingCount: number;
  syncing: boolean;
  lastResult: SyncPushResponse | null;
  syncNow: () => Promise<void>;
  refreshQueue: () => Promise<void>;
}

const SyncContext = createContext<SyncContextValue | null>(null);

export function SyncProvider({ children }: { children: ReactNode }) {
  const online = useNetwork();
  const [pendingCount, setPendingCount] = useState(0);
  const [syncing, setSyncing] = useState(false);
  const [lastResult, setLastResult] = useState<SyncPushResponse | null>(null);

  const refreshQueue = useCallback(async () => {
    const queue = await localDb.getQueue();
    setPendingCount(queue.length);
  }, []);

  const syncNow = useCallback(async () => {
    if (!online || syncing || !localStorage.getItem('access_token')) return;
    const queue = await localDb.getQueue();
    if (!queue.length) { await refreshQueue(); return; }
    setSyncing(true);
    try {
      const { data } = await syncApi.push(queue.map(({ operation_id, record_id, operation_type, base_version, payload }) => ({ operation_id, record_id, operation_type, base_version, payload })));
      setLastResult(data);
      for (const result of data.results) {
        if (result.status === 'success' || result.status === 'conflict') await localDb.removeQueue(result.operation_id);
      }
      await refreshQueue();
    } finally { setSyncing(false); }
  }, [online, syncing, refreshQueue]);

  useEffect(() => { void refreshQueue(); }, [refreshQueue]);
  useEffect(() => { if (online) void syncNow(); }, [online, syncNow]);

  const value = useMemo(() => ({ pendingCount, syncing, lastResult, syncNow, refreshQueue }), [pendingCount, syncing, lastResult, syncNow, refreshQueue]);
  return <SyncContext.Provider value={value}>{children}</SyncContext.Provider>;
}

export const useSync = () => {
  const ctx = useContext(SyncContext);
  if (!ctx) throw new Error('useSync must be used inside SyncProvider');
  return ctx;
};
