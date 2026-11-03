import { useState } from 'react';
import { apiFetch } from '../../utils';

function Registro({ onSwitchLogin }) {
  const [form, setForm] = useState({ nombre: '', apellido: '', email: '', telefono: '', password: '' });
  const [msg, setMsg] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const res = await apiFetch('/api/auth/registro', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(form)
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Error en registro');
      setMsg({ type: 'ok', text: data.message });
      setForm({ nombre: '', apellido: '', email: '', telefono: '', password: '' });
    } catch (err) {
      setMsg({ type: 'error', text: err.message });
    }
  };

  return (
    <div className="form-card" style={{ maxWidth: 400, margin: '0 auto' }}>
      <h2 style={{ marginTop: 0 }}>Crear cuenta</h2>
      {msg && <div style={{ padding: 10, marginBottom: 15, background: msg.type === 'ok' ? 'var(--ok-bg)' : '#FAD4D4', color: msg.type === 'ok' ? 'var(--ok)' : '#D32F2F', borderRadius: 4, fontSize: 13 }}>{msg.text}</div>}
      <form onSubmit={handleSubmit}>
        <div className="grid2">
          <div className="field">
            <label>Nombre</label>
            <input required type="text" value={form.nombre} onChange={e => setForm({ ...form, nombre: e.target.value })} />
          </div>
          <div className="field">
            <label>Apellido</label>
            <input required type="text" value={form.apellido} onChange={e => setForm({ ...form, apellido: e.target.value })} />
          </div>
        </div>
        <div className="field">
          <label>Email</label>
          <input required type="email" value={form.email} onChange={e => setForm({ ...form, email: e.target.value })} />
        </div>
        <div className="field">
          <label>Teléfono (opcional)</label>
          <input type="text" value={form.telefono} onChange={e => setForm({ ...form, telefono: e.target.value })} />
        </div>
        <div className="field">
          <label>Contraseña</label>
          <input required type="password" value={form.password} onChange={e => setForm({ ...form, password: e.target.value })} />
        </div>
        <button type="submit" className="btn primary" style={{ width: '100%', marginTop: 10 }}>Registrarse</button>
      </form>
      <div style={{ marginTop: 20, textAlign: 'center', fontSize: 13 }}>
        ¿Ya tenés cuenta? <button className="btn" style={{ padding: '4px 8px' }} onClick={onSwitchLogin}>Iniciar sesión</button>
      </div>
    </div>
  );
}

export default Registro;
