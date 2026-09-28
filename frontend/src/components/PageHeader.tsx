import { Box, Typography } from '@mui/material';
import type { ReactNode } from 'react';

export function PageHeader({ eyebrow, title, description, action }: { eyebrow?: string; title: string; description?: string; action?: ReactNode }) {
  return <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: { xs: 'flex-start', md: 'center' }, gap: 2, mb: 3, flexWrap: 'wrap' }}>
    <Box>
      {eyebrow && <Typography variant="overline" color="secondary.main" fontWeight={800}>{eyebrow}</Typography>}
      <Typography variant="h4">{title}</Typography>
      {description && <Typography color="text.secondary" sx={{ mt: .6 }}>{description}</Typography>}
    </Box>
    {action}
  </Box>;
}
