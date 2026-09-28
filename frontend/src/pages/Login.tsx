import { useState, type FormEvent } from 'react';
import { Alert, Box, Button, Card, CardContent, Link, Stack, TextField, Typography } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { Brand } from '../components/Brand';
import { useAuth } from '../context/AuthContext';
import { errorMessage } from '../api/client';

export function Login() {
  const navigate = useNavigate(); const { login } = useAuth();
  const [email, setEmail] = useState(''); const [password, setPassword] = useState(''); const [error, setError] = useState(''); const [busy, setBusy] = useState(false);
  const submit = async (e: FormEvent) => { e.preventDefault(); setError(''); setBusy(true); try { await login(email, password); navigate('/'); } catch (err) { setError(errorMessage(err)); } finally { setBusy(false); } };
  return <Box sx={{ minHeight: '100vh', display: 'grid', placeItems: 'center', p: 2, background: 'radial-gradient(circle at 20% 20%, rgba(124,92,255,.2), transparent 30%), radial-gradient(circle at 80% 80%, rgba(32,211,166,.12), transparent 30%), #06101d' }}>
    <Card sx={{ width: '100%', maxWidth: 460, p: { xs: 1, sm: 2 } }}><CardContent sx={{ p: 3 }}>
      <Brand /><Typography variant="h4" sx={{ mt: 5 }}>Welcome back.</Typography><Typography color="text.secondary" sx={{ mt: 1, mb: 3 }}>Enter the control center and keep your data synchronized everywhere.</Typography>
      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
      <Stack component="form" onSubmit={submit} spacing={2}>
        <TextField label="Work email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} required fullWidth />
        <TextField label="Password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} required fullWidth />
        <Button type="submit" variant="contained" size="large" disabled={busy}>{busy ? 'Signing in…' : 'Sign in'}</Button>
      </Stack>
      <Typography color="text.secondary" sx={{ mt: 3 }}>New workspace? <Link component="button" onClick={() => navigate('/register')}>Create an account</Link></Typography>
    </CardContent></Card>
  </Box>;
}
