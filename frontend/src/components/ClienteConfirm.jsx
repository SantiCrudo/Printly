import { useState } from 'react';

function ClienteConfirm({ pedidoData, onNew, onVerSeguimiento }) {
  const [copiado, setCopiado] = useState(false);
  if (!pedidoData) return null;

  const seguimientoUrl = `${window.location.protocol}//${window.location.host}/seguimiento/${pedidoData.token_seguimiento}`;

  const handleCopiarEnlace = async () => {
    try {
      await navigator.clipboard.writeText(seguimientoUrl);
      setCopiado(true);
      setTimeout(() => setCopiado(false), 2500);
    } catch {
      const input = document.createElement('input');
      input.value = seguimientoUrl;
      document.body.appendChild(input);
      input.select();
      document.execCommand('copy');
      document.body.removeChild(input);
      setCopiado(true);
      setTimeout(() => setCopiado(false), 2500);
    }
  };

  return (
    <div id="clienteConfirm" className="confirm">
      <div style={{ fontSize: 13, letterSpacing: '.08em', textTransform: 'uppercase', color: 'var(--text-dim)', fontWeight: 600 }}>
        ¡Pedido enviado con éxito!
      </div>
      <div className="code">{pedidoData.codigo}</div>
      <p style={{ fontSize: 14, color: 'var(--text-dim)', maxWidth: 420, margin: '8px auto 20px', lineHeight: 1.5 }}>
        Guardá tu código para retirar en el mostrador o consultá el estado de tu pedido en vivo.
      </p>
      
      <div className="confirm-actions">
        {onVerSeguimiento && pedidoData.token_seguimiento && (
          <button 
            className="btn stamp" 
            style={{ width: '100%', maxWidth: 280 }}
            onClick={() => onVerSeguimiento(pedidoData.token_seguimiento)}
          >
            Ver estado del pedido →
          </button>
        )}
        <button 
          className="btn" 
          style={{ width: '100%', maxWidth: 280 }}
          onClick={handleCopiarEnlace}
        >
          {copiado ? '✓ ¡Enlace copiado!' : 'Copiar enlace de seguimiento'}
        </button>
        <button 
          className="btn" 
          style={{ width: '100%', maxWidth: 280 }}
          onClick={onNew}
        >
          Hacer otro pedido
        </button>
      </div>
    </div>
  );
}

export default ClienteConfirm;
