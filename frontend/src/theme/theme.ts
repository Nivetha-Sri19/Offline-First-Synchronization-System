import { createTheme } from '@mui/material/styles';

export const theme = createTheme({
  palette: {
    mode: 'dark',
    primary: { main: '#7c5cff' },
    secondary: { main: '#20d3a6' },
    background: { default: '#06101d', paper: '#0b1727' },
    success: { main: '#20d3a6' },
    warning: { main: '#ffbd59' },
    error: { main: '#ff6b81' },
    info: { main: '#4db7ff' },
  },
  typography: {
    fontFamily: 'Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
    h4: { fontWeight: 800, letterSpacing: '-0.03em' },
    h5: { fontWeight: 750 },
    h6: { fontWeight: 700 },
  },
  shape: { borderRadius: 16 },
  components: {
    MuiCard: { styleOverrides: { root: { backgroundImage: 'none', border: '1px solid rgba(255,255,255,.07)', boxShadow: '0 18px 55px rgba(0,0,0,.22)' } } },
    MuiButton: { styleOverrides: { root: { textTransform: 'none', fontWeight: 700, borderRadius: 12 } } },
    MuiTextField: { defaultProps: { size: 'small' } },
    MuiTableCell: { styleOverrides: { root: { borderColor: 'rgba(255,255,255,.06)' } } },
  },
});
