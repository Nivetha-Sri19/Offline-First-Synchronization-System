import { useState } from 'react';
import { Outlet, useLocation, useNavigate } from 'react-router-dom';
import { AppBar, Avatar, Badge, Box, Divider, Drawer, IconButton, List, ListItemButton, ListItemIcon, ListItemText, Menu, MenuItem, Toolbar, Tooltip, Typography, useMediaQuery } from '@mui/material';
import DashboardRoundedIcon from '@mui/icons-material/DashboardRounded';
import DatasetRoundedIcon from '@mui/icons-material/DatasetRounded';
import SyncRoundedIcon from '@mui/icons-material/SyncRounded';
import ReportProblemRoundedIcon from '@mui/icons-material/ReportProblemRounded';
import HistoryRoundedIcon from '@mui/icons-material/HistoryRounded';
import PeopleAltRoundedIcon from '@mui/icons-material/PeopleAltRounded';
import AccountCircleRoundedIcon from '@mui/icons-material/AccountCircleRounded';
import MenuRoundedIcon from '@mui/icons-material/MenuRounded';
import WifiRoundedIcon from '@mui/icons-material/WifiRounded';
import WifiOffRoundedIcon from '@mui/icons-material/WifiOffRounded';
import LogoutRoundedIcon from '@mui/icons-material/LogoutRounded';
import { Brand } from '../components/Brand';
import { useAuth } from '../context/AuthContext';
import { useNetwork } from '../context/NetworkContext';
import { useSync } from '../context/SyncContext';

const drawerWidth = 250;
const items = [
  { label: 'Command Center', path: '/', icon: DashboardRoundedIcon },
  { label: 'Records', path: '/records', icon: DatasetRoundedIcon },
  { label: 'Sync Center', path: '/sync', icon: SyncRoundedIcon },
  { label: 'Conflicts', path: '/conflicts', icon: ReportProblemRoundedIcon },
  { label: 'History', path: '/history', icon: HistoryRoundedIcon },
  { label: 'Users', path: '/users', icon: PeopleAltRoundedIcon },
];

export function AppLayout() {
  const [mobileOpen, setMobileOpen] = useState(false);
  const [anchor, setAnchor] = useState<null | HTMLElement>(null);
  const desktop = useMediaQuery('(min-width:900px)');
  const location = useLocation();
  const navigate = useNavigate();
  const online = useNetwork();
  const { user, logout } = useAuth();
  const { pendingCount, syncing, syncNow } = useSync();

  const drawer = <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column', px: 1.5, py: 2 }}>
    <Box sx={{ px: 1, mb: 3 }}><Brand /></Box>
    <Typography variant="caption" sx={{ px: 1.5, mb: 1, color: 'text.secondary', fontWeight: 800, letterSpacing: '.12em' }}>WORKSPACE</Typography>
    <List sx={{ flex: 1 }}>
      {items.map(({ label, path, icon: Icon }) => {
        const selected = path === '/' ? location.pathname === '/' : location.pathname.startsWith(path);
        return <ListItemButton key={path} selected={selected} onClick={() => { navigate(path); setMobileOpen(false); }} sx={{ mb: .5, borderRadius: 2.5, py: 1.15, '&.Mui-selected': { background: 'linear-gradient(90deg, rgba(124,92,255,.2), rgba(124,92,255,.05))', borderLeft: '3px solid #7c5cff' } }}>
          <ListItemIcon sx={{ minWidth: 40 }}><Icon fontSize="small" /></ListItemIcon><ListItemText primary={label} />
          {label === 'Conflicts' && pendingCount > 0 && <Badge badgeContent={pendingCount} color="warning" />}
        </ListItemButton>;
      })}
    </List>
    <Box sx={{ p: 1.5, borderRadius: 3, bgcolor: 'rgba(255,255,255,.035)', border: '1px solid rgba(255,255,255,.06)' }}>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        {online ? <WifiRoundedIcon color="success" fontSize="small" /> : <WifiOffRoundedIcon color="warning" fontSize="small" />}
        <Typography variant="body2" fontWeight={700}>{online ? 'Connected' : 'Offline mode'}</Typography>
      </Box>
      <Typography variant="caption" color="text.secondary">{syncing ? 'Synchronizing local changes…' : `${pendingCount} local change${pendingCount === 1 ? '' : 's'} pending`}</Typography>
      {online && pendingCount > 0 && <Typography onClick={() => void syncNow()} variant="caption" color="secondary.main" sx={{ display: 'block', mt: .7, cursor: 'pointer', fontWeight: 800 }}>Sync now →</Typography>}
    </Box>
  </Box>;

  return <Box sx={{ minHeight: '100vh', background: 'radial-gradient(circle at 80% -10%, rgba(124,92,255,.13), transparent 30%), #06101d' }}>
    {!desktop && <AppBar position="fixed" elevation={0} sx={{ bgcolor: 'rgba(6,16,29,.85)', backdropFilter: 'blur(16px)' }}><Toolbar><IconButton onClick={() => setMobileOpen(true)}><MenuRoundedIcon /></IconButton><Brand compact /><Box sx={{ flex: 1 }} /><IconButton onClick={(e) => setAnchor(e.currentTarget)}><Avatar sx={{ width: 34, height: 34 }}>{user?.full_name?.charAt(0)}</Avatar></IconButton></Toolbar></AppBar>}
    {desktop ? <Drawer variant="permanent" sx={{ width: drawerWidth, '& .MuiDrawer-paper': { width: drawerWidth, boxSizing: 'border-box', bgcolor: '#081321', borderRight: '1px solid rgba(255,255,255,.06)' } }}>{drawer}</Drawer> : <Drawer open={mobileOpen} onClose={() => setMobileOpen(false)} sx={{ '& .MuiDrawer-paper': { width: drawerWidth, bgcolor: '#081321' } }}>{drawer}</Drawer>}
    <Box sx={{ ml: { md: `${drawerWidth}px` }, pt: { xs: 9, md: 0 } }}>
      {desktop && <AppBar position="sticky" elevation={0} sx={{ bgcolor: 'rgba(6,16,29,.72)', backdropFilter: 'blur(18px)', borderBottom: '1px solid rgba(255,255,255,.05)' }}><Toolbar sx={{ justifyContent: 'flex-end', gap: 1 }}>
        <Tooltip title={online ? 'Connected to network' : 'Offline mode'}><Box sx={{ display: 'flex', alignItems: 'center', gap: .7, mr: 1 }}>{online ? <WifiRoundedIcon color="success" fontSize="small" /> : <WifiOffRoundedIcon color="warning" fontSize="small" />}<Typography variant="caption" color="text.secondary">{online ? 'Online' : 'Offline'}</Typography></Box></Tooltip>
        <Divider orientation="vertical" flexItem />
        <IconButton onClick={(e) => setAnchor(e.currentTarget)}><Avatar sx={{ width: 34, height: 34, bgcolor: 'primary.main' }}>{user?.full_name?.charAt(0)}</Avatar></IconButton>
      </Toolbar></AppBar>}
      <Box component="main" sx={{ p: { xs: 2, md: 3.5 }, maxWidth: 1600, mx: 'auto' }}><Outlet /></Box>
    </Box>
    <Menu anchorEl={anchor} open={Boolean(anchor)} onClose={() => setAnchor(null)}>
      <MenuItem onClick={() => { navigate('/profile'); setAnchor(null); }}><AccountCircleRoundedIcon sx={{ mr: 1 }} fontSize="small" />Profile</MenuItem>
      <MenuItem onClick={() => { logout(); navigate('/login'); }}><LogoutRoundedIcon sx={{ mr: 1 }} fontSize="small" />Sign out</MenuItem>
    </Menu>
  </Box>;
}
