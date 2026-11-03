import { useEffect, useState } from 'react';
import { apiFetch } from '../../utils';

function VerificarEmail({ token, onGoToLogin }) {
  const [status, setStatus] = useState('verificando'); // verificando | ok | error
  const [msg, setMsg] = useState('');

  useEffect(() => {
    async function doVerify() {
      try {
        const res = await apiFetch(`http://localhost:8000/api/auth/verificar/${token}`);
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || 'Error al verificar');
        setStatus('ok');
        setMsg(data.message);
      } catch (err) {
        setStatus('error');
        setMsg(err.message);
      }
    }
    doVerify();
  }, [token]);

  return (
    <div className="form-card" style={{maxWidth: 400, margin: '0 auto', textAlign: 'center'}}>
      <h2 style={{marginTop:0}}>Verificando tu cuenta</h2>
      <p style={{fontSize: 14, color: 'var(--text-dim)'}}>
        {status === 'verificando' && 'Por favor espera...'}
        {status === 'ok' && '¡Excelente! Tu email ha sido verificado.'}
        {status === 'error' && `Error: ${msg}`}
      </p>
      {status !== 'verificando' && (
        <button className="btn primary" onClick={onGoToLogin}>Ir a iniciar sesión</button>
      )}
    </div>
  );
}

export default VerificarEmail;
