import { Navigate, Outlet } from 'react-router-dom'; import { CircularProgress, Stack } from '@mui/material'; import { useAuth } from '../context/AuthContext';
export function ProtectedRoute(){const{user,loading}=useAuth();if(loading)return <Stack alignItems="center" justifyContent="center" minHeight="100vh"><CircularProgress/></Stack>;return user?<Outlet/>:<Navigate to="/login" replace/>}
