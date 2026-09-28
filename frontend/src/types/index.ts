export interface User {
  id: string;
  email: string;
  full_name: string;
  role: string;
  is_active: boolean;
  last_login_at?: string | null;
  created_at: string;
  updated_at: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

export interface RecordItem {
  id: string;
  owner_id: string;
  data: Record<string, unknown>;
  version: number;
  is_deleted: boolean;
  deleted_at?: string | null;
  created_at: string;
  updated_at: string;
  localOnly?: boolean;
  syncState?: 'synced' | 'pending' | 'failed' | 'conflict';
}

export interface Pagination {
  page: number;
  page_size: number;
  total: number;
  total_pages?: number;
}

export interface RecordListResponse {
  items: RecordItem[];
  pagination: Pagination;
}

export interface SyncOperation {
  operation_id: string;
  record_id: string;
  operation_type: 'create' | 'update' | 'delete';
  base_version: number;
  payload: Record<string, unknown> | null;
}

export interface SyncResult {
  operation_id: string;
  record_id: string;
  status: string;
  conflict_status: string;
  server_version?: number | null;
  message?: string | null;
  error?: string | null;
}

export interface SyncPushResponse {
  total_operations: number;
  successful_operations: number;
  failed_operations: number;
  conflict_operations: number;
  results: SyncResult[];
}

export interface SyncStats {
  pending_changes: number;
  successful_syncs: number;
  failed_syncs: number;
  conflicts: number;
  total_syncs: number;
  last_sync_at?: string | null;
}

export interface SyncStatus {
  pending_operations: number;
  processing_operations: number;
  successful_operations: number;
  failed_operations: number;
  unresolved_conflicts: number;
  total_operations: number;
  last_sync_at?: string | null;
  server_timestamp: string;
}

export interface Conflict {
  conflict_id: string;
  record_id: string;
  operation_id: string;
  client_version: number;
  server_version: number;
  client_payload: Record<string, unknown> | null;
  server_payload: Record<string, unknown> | null;
  resolution_strategy?: string | null;
  status: string;
  resolved_by?: string | null;
  resolved_at?: string | null;
  created_at: string;
}

export interface ConflictListResponse {
  items: Conflict[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface HistoryItem {
  sync_id: string;
  operation_id: string;
  record_id: string;
  operation_type: string;
  status: string;
  timestamp: string;
  error_details?: string | null;
  conflict_status: string;
}

export interface HistoryResponse {
  items: HistoryItem[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface SyncPullResponse {
  items: RecordItem[];
  total: number;
  page: number;
  page_size: number;
  has_more: boolean;
  server_timestamp: string;
}
