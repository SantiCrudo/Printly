import { useState, useEffect } from 'react';
import { apiFetch } from '../utils';
import { useAuth } from '../context/AuthContext';
import Ticket from './Ticket';
import Dashboard from './Dashboard';

function NegocioPanel() {
  const { user, login, logout } = useAuth();
  const [activeTab, setActiveTab] = useState('cola'); // cola | dashboard

  const [pedidos, setPedidos] = useState([]);
  const [sucursales, setSucursales] = useState([]);
  const [fetchError, setFetchError] = useState(null);
  
  const [currentFilter, setCurrentFilter] = useState('todos');
  const [sucursalFilter, setSucursalFilter] = useState('todas');

  // Login de operador
  const [opEmail, setOpEmail] = useState('');
  const [opPassword, setOpPassword] = useState('');
  const [loginError, setLoginError] = useState(null);
  const [isLoggingIn, setIsLoggingIn] = useState(false);

  const isOperador = user && (user.rol === 'operador' || user.rol === 'admin');

  const handleOpLogin = async (e) => {
    e.preventDefault();
    setLoginError(null);
    setIsLoggingIn(true);
    const formData = new URLSearchParams();
    formData.append('username', opEmail);
    formData.append('password', opPassword);

    try {
      const res = await apiFetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: formData
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Error al iniciar sesión');
      if (data.usuario && data.usuario.rol !== 'operador' && data.usuario.rol !== 'admin') {
        throw new Error('Esta cuenta no tiene permisos de operador ni administrador');
      }
      login(data.access_token);
    } catch (err) {
      setLoginError(err.message);
    } finally {
      setIsLoggingIn(false);
    }
  };

  const fetchPedidos = async () => {
    if (!isOperador || activeTab !== 'cola') return;
    try {
      const res = await apiFetch('/api/pedidos');
      if (!res.ok) {
        if (res.status === 401 || res.status === 403) {
          setFetchError('No autorizado');
          return;
        }
        throw new Error('Error al obtener pedidos');
      }
      const data = await res.json();
      setPedidos(data);
      setFetchError(null);
    } catch (err) {
      console.error(err);
    }
  };

  const fetchTenant = async () => {
    try {
      const res = await apiFetch('/api/tenant/info');
      const data = await res.json();
      setSucursales(data.sucursales || []);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    if (isOperador) {
      fetchTenant();
      fetchPedidos();
      const timer = setInterval(fetchPedidos, 5000);
      return () => clearInterval(timer);
    }
  }, [activeTab, isOperador]);

  const updateEstado = async (id, nuevoEstado) => {
    setPedidos(pedidos.map(p => p.id === id ? { ...p, estado: nuevoEstado } : p));
    try {
      await apiFetch(`/api/pedidos/${id}/estado`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ estado: nuevoEstado })
      });
    } catch (err) {
      console.error(err);
      fetchPedidos();
    }
  };

  // Si no está logueado como operador/admin, mostrar pantalla de acceso al negocio
  if (!isOperador) {
    return (
      <section id="viewNegocio" className="view active">
        <div className="form-card" style={{maxWidth: 400, margin: '40px auto'}}>
          <h2 style={{marginTop:0}}>Acceso al Panel del Negocio</h2>
          <p style={{fontSize: 13, color: 'var(--text-dim)', marginBottom: 16}}>
            El panel de gestión y cola de producción es exclusivo para operadores y administradores.
          </p>
          {loginError && (
            <div style={{padding:10, marginBottom:15, background: '#FAD4D4', color: '#D32F2F', borderRadius:4, fontSize:13}}>
              {loginError}
            </div>
          )}
          <form onSubmit={handleOpLogin}>
            <div className="field">
              <label>Email de operador</label>
              <input 
                required 
                type="email" 
                placeholder="operador@printly.ar"
                value={opEmail} 
                onChange={e=>setOpEmail(e.target.value)} 
              />
            </div>
            <div className="field">
              <label>Contraseña</label>
              <input 
                required 
                type="password" 
                value={opPassword} 
                onChange={e=>setOpPassword(e.target.value)} 
              />
            </div>
            <button 
              type="submit" 
              className="btn primary" 
              disabled={isLoggingIn}
              style={{width:'100%', marginTop:10}}
            >
              {isLoggingIn ? 'Ingresando...' : 'Ingresar al Panel'}
            </button>
          </form>
        </div>
      </section>
    );
  }

  const visibles = pedidos.filter(p => {
    const matchStatus = currentFilter === 'todos' || p.estado === currentFilter;
    const matchSucursal = sucursalFilter === 'todas' || p.sucursal_id === parseInt(sucursalFilter);
    return matchStatus && matchSucursal;
  });

  return (
    <section id="viewNegocio" className="view active">
      <div style={{display:'flex', justifyContent:'space-between', alignItems:'center', marginBottom: 20}}>
        <div className="tabs">
          <button className={activeTab === 'cola' ? 'active' : ''} onClick={() => setActiveTab('cola')}>Cola de Pedidos</button>
          <button className={activeTab === 'dashboard' ? 'active' : ''} onClick={() => setActiveTab('dashboard')}>Dashboard Estadísticas</button>
        </div>
        <div style={{fontSize: 12, color: 'var(--text-dim)', display:'flex', alignItems:'center', gap: 10}}>
          <span>Sesión: <b>{user.nombre}</b> ({user.rol})</span>
          <button className="btn" style={{padding:'3px 8px', fontSize:11}} onClick={logout}>Salir</button>
        </div>
      </div>

      {fetchError && (
        <div style={{padding:10, marginBottom:15, background: '#FAD4D4', color: '#D32F2F', borderRadius:4}}>
          {fetchError}
        </div>
      )}

      {activeTab === 'cola' && (
        <>
          <div style={{display:'flex', justifyContent:'space-between', alignItems:'center', marginBottom:14}}>
            <h2 className="section" style={{margin:0}}>Cola Operativa</h2>
            {sucursales.length > 1 && (
              <select 
                value={sucursalFilter} 
                onChange={e=>setSucursalFilter(e.target.value)}
                style={{width:'auto', padding:'4px 8px', fontSize:13, borderRadius:4, border:'1px solid var(--line)'}}
              >
                <option value="todas">Todas las sucursales</option>
                {sucursales.map(s => (
                  <option key={s.id} value={s.id}>{s.nombre}</option>
                ))}
              </select>
            )}
          </div>

          <div className="tabs" id="filterTabs" style={{marginBottom: 16}}>
            {['todos', 'recibido', 'en_cola', 'imprimiendo', 'listo', 'entregado'].map(f => (
              <button 
                key={f}
                className={currentFilter === f ? 'active' : ''} 
                onClick={() => setCurrentFilter(f)}
                style={{fontSize: 12, padding: '4px 10px'}}
              >
                {f === 'todos' ? 'Todos' : f.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
              </button>
            ))}
          </div>
          
          <div id="queueList">
            {visibles.length === 0 ? (
              <div className="empty">No hay pedidos en este estado para la sucursal seleccionada.</div>
            ) : (
              visibles.map(p => (
                <Ticket key={p.id} pedido={p} onUpdateEstado={updateEstado} />
              ))
            )}
          </div>
          <iframe id="printFrame" style={{ position: 'fixed', right: '100%', bottom: '100%', width: 0, height: 0, border: 0 }} title="Print Frame" />
        </>
      )}

      {activeTab === 'dashboard' && <Dashboard />}

    </section>
  );
}

export default NegocioPanel;
