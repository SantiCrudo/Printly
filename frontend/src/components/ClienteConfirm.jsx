function ClienteConfirm({ pedidoData, onNew }) {
  if (!pedidoData) return null;

  const handleWhatsApp = () => {
    const link = `${window.location.protocol}//${window.location.host}/seguimiento/${pedidoData.token_seguimiento}`;
    const msg = encodeURIComponent(`Pedido ${pedidoData.codigo} en Printly. Seguí el estado acá: ${link}`);
    window.open('https://wa.me/?text=' + msg, '_blank');
  };

  return (
    <div id="clienteConfirm" className="confirm">
      <div style={{ fontSize: 12, letterSpacing: '.1em', textTransform: 'uppercase', color: 'var(--text-dim)' }}>
        Pedido recibido
      </div>
      <div className="code">{pedidoData.codigo}</div>
      <p style={{ fontSize: 14, color: 'var(--text-dim)', maxWidth: 380, margin: '0 auto 18px' }}>
        Guardá este link para ver el estado sin loguearte, o mandátelo por WhatsApp para no perderlo.
      </p>
      <div style={{ display: 'flex', gap: 10, justifyContent: 'center', flexWrap: 'wrap' }}>
        <button className="btn wa" onClick={handleWhatsApp}>Enviar por WhatsApp</button>
        <button className="btn" onClick={onNew}>Hacer otro pedido</button>
      </div>
    </div>
  );
}

export default ClienteConfirm;
