import { useState, useEffect } from 'react';
import { apiFetch } from '../utils';

const STEPS = [
  { key: 'recibido', label: 'Recibido', desc: 'Ingresó al sistema' },
  { key: 'en_cola', label: 'En cola', desc: 'En espera de impresión' },
  { key: 'imprimiendo', label: 'Imprimiendo', desc: 'En la máquina' },
  { key: 'listo', label: 'Listo', desc: 'Para retirar' }
];

const STATUS_DETAILS = {
  recibido: {
    title: 'Pedido recibido',
    msg: 'Tu pedido ingresó al local. En breve comenzaremos a procesarlo.',
    color: 'var(--text)',
    bg: 'var(--paper-dim)',
    icon: '📥',
    stepIdx: 0
  },
  en_cola: {
    title: 'En cola de impresión',
    msg: 'Tu pedido está preparado y esperando turno en la impresora.',
    color: '#185FA5',
    bg: '#E6F1FB',
    icon: '⏳',
    stepIdx: 1
  },
  imprimiendo: {
    title: 'Imprimiendo ahora',
    msg: 'Tus hojas se están imprimiendo en este momento.',
    color: '#854F0B',
    bg: '#FAEEDA',
    icon: '🖨️',
    stepIdx: 2
  },
  listo: {
    title: '¡Listo para retirar!',
    msg: 'Tus impresiones están listas. Ya podés pasar por el local con tu código.',
    color: '#25543E',
    bg: '#E4EEDA',
    icon: '✅',
    stepIdx: 3
  },
  entregado: {
    title: 'Pedido entregado',
    msg: 'Este trabajo ya fue retirado. ¡Muchas gracias!',
    color: '#4A1B0C',
    bg: '#FAECE7',
    icon: '📦',
    stepIdx: 4
  }
};

function SeguimientoPedido({ token, onVolver }) {
  const [pedido, setPedido] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [copiado, setCopiado] = useState(false);
  const [refreshing, setRefreshing] = useState(false);

  const fetchSeguimiento = async (isManual = false) => {
    if (!token) {
      setError('No se especificó un código o enlace de seguimiento');
      setLoading(false);
      return;
    }
    try {
      if (isManual) setRefreshing(true);
      else setLoading(true);

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
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchSeguimiento();
    // Auto-actualizar cada 15 segundos para ver cambios en vivo
    const timer = setInterval(() => fetchSeguimiento(true), 15000);
    return () => clearInterval(timer);
  }, [token]);

  const handleCopiarEnlace = async () => {
    try {
      await navigator.clipboard.writeText(window.location.href);
      setCopiado(true);
      setTimeout(() => setCopiado(false), 2500);
    } catch {
      const input = document.createElement('input');
      input.value = window.location.href;
      document.body.appendChild(input);
      input.select();
      document.execCommand('copy');
      document.body.removeChild(input);
      setCopiado(true);
      setTimeout(() => setCopiado(false), 2500);
    }
  };

  if (loading) {
    return (
      <div className="form-card tracking-card text-center">
        <div style={{ padding: '32px 16px' }}>
          <div style={{ fontSize: 32, marginBottom: 12 }}>⏳</div>
          <div style={{ fontSize: 16, fontWeight: 600 }}>Cargando estado del pedido...</div>
          <p style={{ fontSize: 13, color: 'var(--text-dim)', marginTop: 6 }}>Buscando información en tiempo real</p>
        </div>
      </div>
    );
  }

  if (error || !pedido) {
    return (
      <div className="form-card tracking-card text-center">
        <div style={{ padding: '24px 16px' }}>
          <div style={{ fontSize: 32, marginBottom: 10 }}>❌</div>
          <h2 style={{ color: 'var(--stamp)', margin: '0 0 8px', fontSize: 20 }}>Pedido no encontrado</h2>
          <p style={{ color: 'var(--text-dim)', fontSize: 14, margin: '0 0 20px' }}>
            {error || 'No pudimos encontrar el pedido con este enlace.'}
          </p>
          <button className="btn primary" onClick={onVolver} style={{ minWidth: 160 }}>
            Volver al inicio
          </button>
        </div>
      </div>
    );
  }

  const currentInfo = STATUS_DETAILS[pedido.estado] || STATUS_DETAILS.recibido;
  const currentStep = currentInfo.stepIdx;
  const isListo = pedido.estado === 'listo';
  const fmt = (n) => '$' + Number(n).toLocaleString('es-AR', { minimumFractionDigits: 0, maximumFractionDigits: 2 });

  return (
    <div className="form-card tracking-card">
      {/* Cabecera de estado principal */}
      <div 
        className="tracking-status-banner"
        style={{
          background: currentInfo.bg,
          color: currentInfo.color,
          border: `1px solid ${currentInfo.color}30`
        }}
      >
        <div className="tracking-icon">{currentInfo.icon}</div>
        <div className="tracking-status-text">
          <div className="tracking-status-title">{currentInfo.title}</div>
          <div className="tracking-status-sub">{currentInfo.msg}</div>
        </div>
      </div>

      {/* Stepper simplificado y adaptable */}
      {pedido.estado !== 'entregado' ? (
        <div className="tracking-progress-container">
          <div className="tracking-step-bar">
            {STEPS.map((step, idx) => {
              const isCompleted = currentStep >= idx;
              const isCurrent = currentStep === idx;
              return (
                <div key={step.key} className={`tracking-step-col ${isCompleted ? 'completed' : ''} ${isCurrent ? 'active' : ''}`}>
                  <div className="tracking-step-dot">
                    {isCompleted ? '✓' : idx + 1}
                  </div>
                  <div className="tracking-step-label">{step.label}</div>
                </div>
              );
            })}
          </div>
        </div>
      ) : (
        <div style={{ textAlign: 'center', margin: '14px 0', fontSize: 13, color: 'var(--text-dim)' }}>
          Este pedido fue completado y entregado.
        </div>
      )}

      {/* Código de retiro grande y legible para mostrador */}
      <div className={`tracking-pickup-box ${isListo ? 'ready-pulse' : ''}`}>
        <div className="tracking-pickup-tag">Código para retirar</div>
        <div className="tracking-pickup-code">{pedido.codigo}</div>
        <div className="tracking-pickup-hint">
          {isListo ? 'Mostrá este código en el mostrador para retirar' : 'Guardá este código para retirarlo cuando esté listo'}
        </div>
      </div>

      {/* Detalles claros y directos */}
      <div className="tracking-info-grid">
        <div className="tracking-info-item">
          <span className="tracking-label">📍 Sucursal de retiro</span>
          <div className="tracking-val-highlight">{pedido.sucursal_nombre}</div>
          {pedido.sucursal_direccion && (
            <div className="tracking-subval">{pedido.sucursal_direccion}</div>
          )}
        </div>

        <div className="tracking-info-item">
          <span className="tracking-label">💰 Total a pagar</span>
          <div className="tracking-val-highlight" style={{ color: 'var(--stamp)' }}>
            {fmt(pedido.precio_estimado)}
          </div>
          <div className="tracking-subval">Se abona al retirar</div>
        </div>

        <div className="tracking-info-item tracking-full-col">
          <span className="tracking-label">📄 Resumen de impresión</span>
          <div className="tracking-val">
            <b>{pedido.cantidad_copias} {pedido.cantidad_copias === 1 ? 'copia' : 'copias'}</b> · {pedido.tamano_papel} · {pedido.color ? 'A color' : 'Blanco y negro'} · {pedido.doble_faz ? 'Doble faz' : 'Simple faz'}
          </div>
          {pedido.descripcion_trabajo && (
            <div className="tracking-note">
              <i>Nota: "{pedido.descripcion_trabajo}"</i>
            </div>
          )}
        </div>
      </div>

      {/* Acciones directas y sin WhatsApp */}
      <div className="tracking-actions">
        <button 
          className="btn" 
          onClick={handleCopiarEnlace}
          style={{ width: '100%' }}
        >
          {copiado ? '✓ ¡Enlace copiado al portapapeles!' : '🔗 Copiar enlace de seguimiento'}
        </button>

        <div style={{ display: 'flex', gap: 8, width: '100%' }}>
          <button 
            className="btn" 
            onClick={() => fetchSeguimiento(true)} 
            disabled={refreshing}
            style={{ flex: 1 }}
          >
            {refreshing ? 'Actualizando...' : '↻ Actualizar'}
          </button>
          
          <button 
            className="btn primary" 
            onClick={onVolver}
            style={{ flex: 1 }}
          >
            Hacer otro pedido
          </button>
        </div>
      </div>
    </div>
  );
}

export default SeguimientoPedido;
