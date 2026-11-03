import { useState, useEffect } from 'react';
import { apiFetch } from '../utils';
import { useAuth } from '../context/AuthContext';
import ClienteForm from './ClienteForm';
import ClienteConfirm from './ClienteConfirm';

function PanelCliente() {
  const { user, token, logout } = useAuth();
  const [pedidos, setPedidos] = useState([]);
  const [view, setView] = useState('list'); // list | new | confirm
  const [pedidoConfirmado, setPedidoConfirmado] = useState(null);

  const fetchPedidos = async () => {
    try {
      const res = await apiFetch('/api/pedidos/mis-pedidos', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const data = await res.json();
      setPedidos(data);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    if (view === 'list') fetchPedidos();
  }, [view]);

  const handleRepetir = async (id) => {
    try {
      const res = await apiFetch(`/api/pedidos/${id}/repetir`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const data = await res.json();
      if (!res.ok) throw new Error('Error al repetir pedido');
      setPedidoConfirmado(data);
      setView('confirm');
    } catch (e) {
      alert(e.message);
    }
  };

  const fmt = (n) => '$' + n.toLocaleString('es-AR');
  const estadoLabel = { recibido: 'Recibido', en_cola: 'En cola', imprimiendo: 'Imprimiendo', listo: 'Listo para retirar', entregado: 'Entregado' };

  if (view === 'new') {
    return (
      <div>
        <button className="btn" onClick={() => setView('list')} style={{ marginBottom: 16 }}>← Volver a mis pedidos</button>
        <ClienteForm onConfirm={(data) => {
          setPedidoConfirmado(data);
          setView('confirm');
        }} />
      </div>
    );
  }

  if (view === 'confirm') {
    return (
      <ClienteConfirm 
        pedidoData={pedidoConfirmado} 
        onNew={() => setView('list')} 
        onVerSeguimiento={(token) => {
          window.location.href = `/seguimiento/${token}`;
        }}
      />
    );
  }

  return (
    <div id="panelCliente">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 10, marginBottom: 20 }}>
        <h2 className="section" style={{ margin: 0 }}>Mis Pedidos</h2>
        <div style={{ display: 'flex', gap: 10 }}>
          <button className="btn primary" onClick={() => setView('new')}>+ Nuevo pedido</button>
          <button className="btn" onClick={logout}>Cerrar sesión</button>
        </div>
      </div>

      <div className="form-card">
        <p style={{ marginTop: 0, marginBottom: 20, fontSize: 14, color: 'var(--text-dim)' }}>
          Hola {user.nombre}, este es tu historial de impresiones.
        </p>

        {pedidos.length === 0 ? (
          <div className="empty">Aún no hiciste pedidos.</div>
        ) : (
          <div style={{ display: 'grid', gap: 12 }}>
            {pedidos.map(p => (
              <div key={p.id} style={{ padding: 16, border: '1px solid var(--line)', borderRadius: 6 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
                  <strong style={{ fontFamily: 'monospace' }}>{p.codigo}</strong>
                  <span className={`stamp-badge st-${p.estado}`} style={{ fontSize: 9, padding: '2px 6px' }}>{estadoLabel[p.estado]}</span>
                </div>
                <div style={{ fontSize: 13, color: 'var(--text)', marginBottom: 4 }}>
                  <b>{p.fileName}</b> - {p.desc || 'Sin descripción'}
                </div>
                <div className="meta-row" style={{ marginTop: 6 }}>
                  <span>{p.copias} juegos</span>
                  <span>{p.paginas} pág.</span>
                  <span>{p.color ? 'Color' : 'B/N'}</span>
                  <span>{p.tamano} {p.dobleFaz ? '· Doble faz' : ''}</span>
                  <span><b>{fmt(p.precio)}</b></span>
                </div>
                <div style={{ marginTop: 12, borderTop: '1px dashed var(--line)', paddingTop: 12 }}>
                  <button className="btn" style={{ fontSize: 11, padding: '6px 10px' }} onClick={() => handleRepetir(p.id)}>
                    Repetir pedido
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default PanelCliente;
