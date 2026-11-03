import { getApiUrl, apiFetch } from '../utils';

const ESTADOS = ['recibido', 'en_cola', 'imprimiendo', 'listo', 'entregado'];
const ESTADO_LABEL = { recibido: 'Recibido', en_cola: 'En cola', imprimiendo: 'Imprimiendo', listo: 'Listo para retirar', entregado: 'Entregado' };

function Ticket({ pedido, onUpdateEstado }) {
  const fmt = (n) => '$' + n.toLocaleString('es-AR');
  const d = new Date(pedido.creado);
  const timeStr = d.toLocaleTimeString('es-AR', { hour: '2-digit', minute: '2-digit' });

  const fileUrl = getApiUrl(`/api/archivos/${pedido.fileId}?token=${pedido.token}`);

  const previewPedido = () => {
    window.open(fileUrl, '_blank');
  };

  const imprimirPedido = async () => {
    try {
      const res = await apiFetch(fileUrl);
      if (!res.ok) throw new Error('No se pudo obtener el archivo para imprimir');
      const blob = await res.blob();
      const blobUrl = URL.createObjectURL(blob);

      const frame = document.getElementById('printFrame');
      if (frame) {
        frame.onload = () => {
          try {
            frame.contentWindow.focus();
            frame.contentWindow.print();
          } catch (e) {
            console.warn('Fallback al imprimir:', e);
            const w = window.open(blobUrl, '_blank');
            if (w) {
              w.focus();
              setTimeout(() => { try { w.print(); } catch (_) {} }, 500);
            }
          }
        };
        frame.src = blobUrl;
      } else {
        const w = window.open(blobUrl, '_blank');
        if (w) {
          w.focus();
          setTimeout(() => { try { w.print(); } catch (_) {} }, 500);
        }
      }
    } catch (err) {
      console.error('Error al imprimir pedido:', err);
      window.open(fileUrl, '_blank');
    }

    if (pedido.estado === 'recibido') onUpdateEstado(pedido.id, 'en_cola');
    if (pedido.estado === 'en_cola') onUpdateEstado(pedido.id, 'imprimiendo');
  };

  const avanzarEstado = () => {
    const i = ESTADOS.indexOf(pedido.estado);
    if (i < ESTADOS.length - 1) onUpdateEstado(pedido.id, ESTADOS[i + 1]);
  };

  return (
    <div className="ticket">
      <div className="ticket-head">
        <div>
          <div className="ticket-code">{pedido.codigo} · {timeStr}</div>
          <div style={{ marginTop: 6, display: 'flex', gap: 8, alignItems: 'center' }}>
            <b>{pedido.nombre}</b>
            <span className={`badge-tipo badge-${pedido.tipo}`}>{pedido.tipo}</span>
          </div>
        </div>
        <span className={`stamp-badge st-${pedido.estado}`}>{ESTADO_LABEL[pedido.estado]}</span>
      </div>

      <div className="ticket-body">
        {pedido.desc ? pedido.desc : 'Sin descripción adicional.'}
        <div className="meta-row">
          <span>{pedido.copias} copia(s)</span>
          <span>{pedido.paginas} pág.</span>
          <span>{pedido.color ? 'Color' : 'B/N'}</span>
          <span>{pedido.tamano}{pedido.dobleFaz ? ' · doble faz' : ''}</span>
          <span><b>{fmt(pedido.precio)}</b></span>
        </div>
        <div className="file-row">
          <span className="dot"></span>
          <span style={{ wordBreak: 'break-all' }}>{pedido.fileName}</span>
        </div>
      </div>

      <div className="ticket-actions">
        <button className="btn" onClick={previewPedido}>Vista previa</button>
        <button className="btn stamp" onClick={imprimirPedido} disabled={pedido.estado === 'entregado'}>Imprimir</button>
        <button className="btn primary" onClick={avanzarEstado} disabled={pedido.estado === 'entregado'}>Siguiente estado →</button>
      </div>
    </div>
  );
}

export default Ticket;
