import { openDB, type DBSchema } from 'idb';
import type { RecordItem, SyncOperation } from '../types';

interface SyncDB extends DBSchema {
  records: { key: string; value: RecordItem };
  queue: { key: string; value: SyncOperation & { createdAt: string; attempts: number; lastError?: string } };
  meta: { key: string; value: string };
}

const dbPromise = openDB<SyncDB>('syncsphere-db', 1, {
  upgrade(db) {
    db.createObjectStore('records');
    db.createObjectStore('queue');
    db.createObjectStore('meta');
  },
});

export const localDb = {
  async putRecord(record: RecordItem) {
    const db = await dbPromise;
    await db.put('records', record, record.id);
  },
  async putRecords(records: RecordItem[]) {
    const db = await dbPromise;
    const tx = db.transaction('records', 'readwrite');
    for (const record of records) await tx.store.put(record, record.id);
    await tx.done;
  },
  async getRecords() {
    const db = await dbPromise;
    return db.getAll('records');
  },
  async deleteRecord(id: string) {
    const db = await dbPromise;
    await db.delete('records', id);
  },
  async enqueue(operation: SyncOperation) {
    const db = await dbPromise;
    await db.put('queue', { ...operation, createdAt: new Date().toISOString(), attempts: 0 }, operation.operation_id);
  },
  async getQueue() {
    const db = await dbPromise;
    return db.getAll('queue');
  },
  async removeQueue(operationId: string) {
    const db = await dbPromise;
    await db.delete('queue', operationId);
  },
  async setMeta(key: string, value: string) {
    const db = await dbPromise;
    await db.put('meta', value, key);
  },
  async getMeta(key: string) {
    const db = await dbPromise;
    return db.get('meta', key);
  },
};
