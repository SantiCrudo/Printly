import { useState, useEffect } from 'react';
import { apiFetch } from '../utils';

const STEPS = [
  { key: 'recibido', label: 'Recibido' },
  { key: 'en_cola', label: 'En cola' },
  { key: 'imprimiendo', label: 'Imprimiendo' },
  { key: 'listo', label: 'Listo para retirar' },
  { key: 'entregado', label: 'Entregado' }
];

function SeguimientoPedido({ token, onVolver }) {
  const [pedido, setPedido] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function fetchSeguimiento() {
      if (!token) {
        setError('No se especificó un token de seguimiento');
        setLoading(false);
        return;
      }
      try {
        setLoading(true);
        const res = await apiFetch(`/api/pedidos/seguimiento/${token}`);
        if (!res.ok) {
          if (res.status === 404) throw new Error('Pedido no encontrado o enlace incorrecto');
          throw new Error('Error al consultar el estado del pedido');
        }
        const data = await res.json();
        setPedido(data);
        setError(null);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }
    fetchSeguimiento();
  }, [token]);

  if (loading) {
    return (
      <div className="form-card" style={{maxWidth: 500, margin: '40px auto', textAlign: 'center'}}>
        <p>Cargando información del pedido...</p>
      </div>
    );
  }

  if (error || !pedido) {
    return (
      <div className="form-card" style={{maxWidth: 500, margin: '40px auto', textAlign: 'center'}}>
        <h2 style={{color: '#D32F2F', marginTop: 0}}>Pedido no encontrado</h2>
        <p style={{color: 'var(--text-dim)', fontSize: 14}}>{error || 'No se pudo cargar el pedido.'}</p>
        <button className="btn" onClick={onVolver} style={{marginTop: 15}}>
          Volver al inicio
        </button>
      </div>
    );
  }

  const currentIndex = STEPS.findIndex(s => s.key === pedido.estado);
  const fmt = (n) => '$' + Number(n).toLocaleString('es-AR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  const fechaStr = pedido.creado_en ? new Date(pedido.creado_en).toLocaleString('es-AR', {
    day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit'
  }) : '';

  const shareWhatsapp = () => {
    const link = window.location.href;
    const msg = encodeURIComponent(`Hola! Seguí mi pedido ${pedido.codigo} en Printly: ${link}`);
    window.open(`https://wa.me/?text=${msg}`, '_blank');
  };

  return (
    <div className="form-card" style={{maxWidth: 540, margin: '30px auto'}}>
      <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid var(--line)', paddingBottom: 12}}>
        <div>
          <span style={{fontSize: 11, textTransform: 'uppercase', letterSpacing: '.08em', color: 'var(--text-dim)'}}>
            Seguimiento en vivo
          </span>
          <h2 style={{margin: '2px 0 0', fontSize: 24}}>{pedido.codigo}</h2>
        </div>
        <div style={{textAlign: 'right'}}>
          <span style={{fontSize: 11, color: 'var(--text-dim)'}}>Total estimado</span>
          <div style={{fontSize: 20, fontWeight: 700, color: 'var(--accent)'}}>
            {fmt(pedido.precio_estimado)}
          </div>
        </div>
      </div>

      {/* Stepper horizontal */}
      <div style={{margin: '24px 0'}}>
        <div style={{display: 'flex', justifyContent: 'space-between', position: 'relative', marginBottom: 8}}>
          {STEPS.map((step, idx) => {
            const isDone = currentIndex >= idx;
            const isCurrent = currentIndex === idx;
            return (
              <div key={step.key} style={{flex: 1, textAlign: 'center', position: 'relative'}}>
                <div style={{
                  width: 28,
                  height: 28,
                  borderRadius: '50%',
                  background: isDone ? 'var(--accent, #1976D2)' : '#e0e0e0',
                  color: isDone ? '#fff' : '#666',
                  display: 'inline-flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: 12,
                  fontWeight: 'bold',
                  boxShadow: isCurrent ? '0 0 0 4px rgba(25, 118, 210, 0.2)' : 'none',
                  transition: 'all 0.3s'
                }}>
                  {idx + 1}
                </div>
                <div style={{
                  fontSize: 11,
                  marginTop: 6,
                  fontWeight: isCurrent ? 700 : 400,
                  color: isCurrent ? 'var(--text)' : 'var(--text-dim)'
                }}>
                  {step.label}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Detalles del pedido */}
      <div style={{background: 'var(--paper, #fafafa)', border: '1px solid var(--line)', borderRadius: 6, padding: 14, fontSize: 13, display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10}}>
        <div>
          <span style={{color: 'var(--text-dim)'}}>Sucursal de retiro:</span>
          <div style={{fontWeight: 600}}>{pedido.sucursal_nombre}</div>
          {pedido.sucursal_direccion && (
            <div style={{fontSize: 12, color: 'var(--text-dim)'}}>{pedido.sucursal_direccion}</div>
          )}
        </div>
        <div>
          <span style={{color: 'var(--text-dim)'}}>Fecha y hora:</span>
          <div style={{fontWeight: 600}}>{fechaStr}</div>
        </div>
        <div>
          <span style={{color: 'var(--text-dim)'}}>Configuración:</span>
          <div>
            {pedido.cantidad_copias} copia(s) · {pedido.tamano_papel} · {pedido.color ? 'Color' : 'B/N'} · {pedido.doble_faz ? 'Doble faz' : 'Simple faz'}
          </div>
        </div>
        <div>
          <span style={{color: 'var(--text-dim)'}}>Estado actual:</span>
          <div style={{fontWeight: 600, textTransform: 'capitalize'}}>
            {STEPS.find(s => s.key === pedido.estado)?.label || pedido.estado}
          </div>
        </div>
      </div>

      <div style={{marginTop: 20, display: 'flex', gap: 10, justifyContent: 'center', flexWrap: 'wrap'}}>
        <button className="btn wa" onClick={shareWhatsapp}>
          Guardar / Compartir por WhatsApp
        </button>
        <button className="btn" onClick={onVolver}>
          Hacer otro pedido
        </button>
      </div>
    </div>
  );
}

export default SeguimientoPedido;

