import { api } from './client';
import type { ConflictListResponse, HistoryResponse, RecordItem, RecordListResponse, SyncBatchResponse, SyncOperation, SyncPullResponse, SyncStats, SyncStatus, TokenResponse, User } from '../types';

export const authApi = {
  login: (body: { email: string; password: string }) => api.post<TokenResponse>('/auth/login', body),
  register: (body: { email: string; password: string; full_name: string }) => api.post<User>('/auth/register', body),
  me: () => api.get<User>('/auth/me'),
};

export const recordsApi = {
  list: (params: Record<string, string | number | undefined>) => api.get<RecordListResponse>('/records', { params }),
  get: (id: string) => api.get<RecordItem>(`/records/${id}`),
  create: (data: Record<string, unknown>) => api.post<RecordItem>('/records', { data }),
  update: (id: string, data: Record<string, unknown>, expected_version: number) => api.patch<RecordItem>(`/records/${id}`, { data, expected_version }),
  remove: (id: string, expected_version: number) => api.delete<RecordItem>(`/records/${id}`, { data: { expected_version } }),
};

export const syncApi = {
  pull: (params: Record<string, string | number | undefined>) => api.get<SyncPullResponse>('/sync/pull', { params }),
  push: async (operations: SyncOperation[]) => {
    try { return await api.post<SyncBatchResponse>('/sync/push', { operations }); }
    catch (error) { if (error && typeof error === 'object' && 'response' in error && (error as any).response?.status === 404) return api.post<SyncBatchResponse>('/sync/batch', { operations }); throw error; }
  },
  status: async () => {
    try { return await api.get<SyncStatus>('/sync/status'); }
    catch (error) {
      if (error && typeof error === 'object' && 'response' in error && (error as any).response?.status === 404) {
        const { data } = await api.get<SyncStats>('/dashboard/summary');
        return { data: { pending_operations: data.pending_changes, processing_operations: 0, successful_operations: data.successful_syncs, failed_operations: data.failed_syncs, unresolved_conflicts: data.conflicts, total_operations: data.total_syncs, last_sync_at: data.last_sync_at, server_timestamp: new Date().toISOString() } } as any;
      }
      throw error;
    }
  },
  conflicts: async (params?: Record<string, string | number | undefined>) => {
    try { return await api.get<ConflictListResponse>('/sync/conflicts', { params }); }
    catch (error) { if (error && typeof error === 'object' && 'response' in error && (error as any).response?.status === 404) return api.get<ConflictListResponse>('/conflicts', { params }); throw error; }
  },
  resolve: async (id: string, body: { strategy: string; resolved_data?: Record<string, unknown> }) => {
    try { return await api.post(`/sync/conflicts/${id}/resolve`, body); }
    catch (error) { if (error && typeof error === 'object' && 'response' in error && (error as any).response?.status === 404) return api.post(`/conflicts/${id}/resolve`, body); throw error; }
  },
  history: async (params?: Record<string, string | number | undefined>) => {
    try { return await api.get<HistoryResponse>('/sync/history', { params }); }
    catch (error) {
      if (error && typeof error === 'object' && 'response' in error && (error as any).response?.status === 404) {
        const response = await api.get<HistoryItem[]>('/sync-history', { params });
        return { data: { items: response.data, total: response.data.length, page: Number(params?.page ?? 1), page_size: Number(params?.page_size ?? 20), total_pages: response.data.length ? 1 : 0 } };
      }
      throw error;
    }
  },
};

export const dashboardApi = {
  stats: async () => {
    try { return await api.get<SyncStats>('/dashboard/stats'); }
    catch (error) { if (error && typeof error === 'object' && 'response' in error && (error as any).response?.status === 404) return api.get<SyncStats>('/dashboard/summary'); throw error; }
  },
};

export const usersApi = {
  list: (params?: Record<string, string | number | undefined>) => api.get<User[]>('/users', { params }),
  get: (id: string) => api.get<User>(`/users/${id}`),
  create: (body: { email: string; password: string; full_name: string }) => api.post<User>('/users', body),
};
