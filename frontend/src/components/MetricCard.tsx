import { Box, Card, CardContent, Typography } from '@mui/material';
import type { SvgIconComponent } from '@mui/icons-material';

export function MetricCard({ title, value, subtitle, icon: Icon, tone = 'primary' }: { title: string; value: string | number; subtitle?: string; icon: SvgIconComponent; tone?: 'primary' | 'success' | 'warning' | 'error' }) {
  return <Card sx={{ height: '100%', position: 'relative', overflow: 'hidden' }}>
    <Box sx={{ position: 'absolute', width: 110, height: 110, borderRadius: '50%', right: -45, top: -50, background: `radial-gradient(circle, rgba(${tone === 'primary' ? '124,92,255' : tone === 'success' ? '32,211,166' : tone === 'warning' ? '255,189,89' : '255,107,129'},.20), transparent 68%)` }} />
    <CardContent sx={{ p: 2.5 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
        <Box><Typography variant="body2" color="text.secondary">{title}</Typography><Typography variant="h4" sx={{ mt: .8 }}>{value}</Typography></Box>
        <Box sx={{ width: 42, height: 42, borderRadius: 2.5, display: 'grid', placeItems: 'center', bgcolor: 'rgba(255,255,255,.06)' }}><Icon fontSize="small" /></Box>
      </Box>
      {subtitle && <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 1.2 }}>{subtitle}</Typography>}
    </CardContent>
  </Card>;
}
