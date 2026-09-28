import { useState, type FormEvent } from 'react';
import { Alert, Box, Button, Card, CardContent, Link, Stack, TextField, Typography } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { Brand } from '../components/Brand';
import { useAuth } from '../context/AuthContext';
import { errorMessage } from '../api/client';

export function Register() {
  const navigate = useNavigate(); const { register } = useAuth();
  const [form, setForm] = useState({ full_name: '', email: '', password: '' }); const [error, setError] = useState(''); const [busy, setBusy] = useState(false);
  const submit = async (e: FormEvent) => { e.preventDefault(); setError(''); setBusy(true); try { await register(form.email, form.password, form.full_name); navigate('/'); } catch (err) { setError(errorMessage(err)); } finally { setBusy(false); } };
  return <Box sx={{ minHeight: '100vh', display: 'grid', placeItems: 'center', p: 2, background: 'radial-gradient(circle at 80% 10%, rgba(32,211,166,.16), transparent 30%), #06101d' }}>
    <Card sx={{ width: '100%', maxWidth: 500 }}><CardContent sx={{ p: 4 }}><Brand /><Typography variant="h4" sx={{ mt: 5 }}>Build your workspace.</Typography><Typography color="text.secondary" sx={{ mt: 1, mb: 3 }}>Start with a secure account. Your local data can continue working when the network cannot.</Typography>
      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
      <Stack component="form" onSubmit={submit} spacing={2}><TextField label="Full name" value={form.full_name} onChange={(e) => setForm({ ...form, full_name: e.target.value })} required /><TextField label="Email" type="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} required /><TextField label="Password" type="password" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} required helperText="Minimum 8 characters" /><Button type="submit" variant="contained" size="large" disabled={busy}>{busy ? 'Creating…' : 'Create workspace'}</Button></Stack>
      <Typography color="text.secondary" sx={{ mt: 3 }}>Already registered? <Link component="button" onClick={() => navigate('/login')}>Sign in</Link></Typography>
    </CardContent></Card>
  </Box>;
}
