import { Chip } from '@mui/material';

export function StatusPill({ status }: { status: string }) {
  const s = status.toLowerCase();
  const color = s.includes('success') || s.includes('resolved') || s === 'synced' ? 'success' : s.includes('fail') || s.includes('error') ? 'error' : s.includes('conflict') || s.includes('unresolved') || s.includes('pending') ? 'warning' : 'default';
  return <Chip size="small" label={status.replaceAll('_', ' ')} color={color} variant="outlined" sx={{ textTransform: 'capitalize', fontWeight: 700 }} />;
}
