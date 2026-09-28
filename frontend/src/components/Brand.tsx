import { Box, Typography } from '@mui/material';
import HubOutlinedIcon from '@mui/icons-material/HubOutlined';

export function Brand({ compact = false }: { compact?: boolean }) {
  return <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.25 }}>
    <Box sx={{ width: 40, height: 40, borderRadius: 2.5, display: 'grid', placeItems: 'center', background: 'linear-gradient(135deg,#7c5cff,#20d3a6)', boxShadow: '0 10px 30px rgba(124,92,255,.25)' }}>
      <HubOutlinedIcon sx={{ color: '#fff' }} />
    </Box>
    {!compact && <Box><Typography fontWeight={850} lineHeight={1}>SyncSphere</Typography><Typography variant="caption" color="text.secondary">OFFLINE-FIRST CONTROL</Typography></Box>}
  </Box>;
}
