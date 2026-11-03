import { useState } from 'react';
import { apiFetch } from '../../utils';
import { useAuth } from '../../context/AuthContext';

function Login({ onSwitchRegistro, onLoginSuccess }) {
  const { login } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    const formData = new URLSearchParams();
    formData.append('username', email); // OAuth2 expects 'username'
    formData.append('password', password);

    try {
      const res = await apiFetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: formData
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Error al iniciar sesión');

      login(data.access_token);
      if (onLoginSuccess) onLoginSuccess();
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div className="form-card" style={{ maxWidth: 400, margin: '0 auto' }}>
      <h2 style={{ marginTop: 0 }}>Iniciar Sesión</h2>
      {error && <div style={{ padding: 10, marginBottom: 15, background: '#FAD4D4', color: '#D32F2F', borderRadius: 4, fontSize: 13 }}>{error}</div>}
      <form onSubmit={handleSubmit}>
        <div className="field">
          <label>Email</label>
          <input required type="email" value={email} onChange={e => setEmail(e.target.value)} />
        </div>
        <div className="field">
          <label>Contraseña</label>
          <input required type="password" value={password} onChange={e => setPassword(e.target.value)} />
        </div>
        <button type="submit" className="btn primary" style={{ width: '100%', marginTop: 10 }}>Ingresar</button>
      </form>
      <div style={{ marginTop: 20, textAlign: 'center', fontSize: 13 }}>
        ¿No tenés cuenta? <button className="btn" style={{ padding: '4px 8px' }} onClick={onSwitchRegistro}>Registrarse</button>
      </div>
    </div>
  );
}

export default Login;
