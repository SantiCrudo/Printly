import { useState, useEffect } from 'react';
import { AuthProvider, useAuth } from './context/AuthContext';
import { getTenantHost } from './utils';
import ClienteForm from './components/ClienteForm';
import ClienteConfirm from './components/ClienteConfirm';
import NegocioPanel from './components/NegocioPanel';
import Registro from './components/auth/Registro';
import Login from './components/auth/Login';
import VerificarEmail from './components/auth/VerificarEmail';
import PanelCliente from './components/PanelCliente';
import SeguimientoPedido from './components/SeguimientoPedido';
import './index.css';

function AppContent() {
  const { user, loading } = useAuth();
  const [view, setView] = useState('Cliente'); // Cliente | Negocio | Auth | MiPanel | Seguimiento
  const [authMode, setAuthMode] = useState('login'); // login | registro | verificar
  const [pedidoConfirmado, setPedidoConfirmado] = useState(null);
  const [seguimientoToken, setSeguimientoToken] = useState(null);

  useEffect(() => {
    const handleLocationChange = () => {
      const urlPath = window.location.pathname;
      if (urlPath.startsWith('/verificar/')) {
        setView('Auth');
        setAuthMode('verificar');
      } else if (urlPath.startsWith('/seguimiento/')) {
        const token = urlPath.split('/')[2];
        if (token) {
          setSeguimientoToken(token);
          setView('Seguimiento');
        }
      }
    };

    handleLocationChange();
    window.addEventListener('popstate', handleLocationChange);
    return () => window.removeEventListener('popstate', handleLocationChange);
  }, []);

  const handleConfirm = (data) => {
    setPedidoConfirmado(data);
  };

  const handleNewOrder = () => {
    setPedidoConfirmado(null);
    setSeguimientoToken(null);
    window.history.pushState({}, '', '/');
    setView('Cliente');
  };

  const navigateTo = (newView) => {
    if (newView === 'Cliente') {
      window.history.pushState({}, '', '/');
    }
    setView(newView);
  };

  if (loading) return <div style={{padding:40, textAlign:'center'}}>Cargando...</div>;

  return (
    <>
      <header>
        <div className="brand" onClick={() => navigateTo('Cliente')} style={{cursor: 'pointer'}}>
          <div className="mark">P</div>
          <div>
            <h1>Printly</h1>
            <span>{getTenantHost()}</span>
          </div>
        </div>
        <nav>
          <button 
            className={view === 'Cliente' ? 'active' : ''} 
            onClick={() => navigateTo('Cliente')}
          >
            Hacer pedido
          </button>

          {!user ? (
            <button 
              className={view === 'Auth' ? 'active' : ''} 
              onClick={() => {setView('Auth'); setAuthMode('login');}}
            >
              Ingresar
            </button>
          ) : (
            <button 
              className={view === 'MiPanel' ? 'active' : ''} 
              onClick={() => navigateTo('MiPanel')}
            >
              Mis pedidos
            </button>
          )}

          <button 
            className={view === 'Negocio' ? 'active' : ''} 
            onClick={() => navigateTo('Negocio')}
          >
            Negocio
          </button>
        </nav>
      </header>

      <main>
        {view === 'Cliente' && (
          <section id="viewCliente" className="view active">
            {!pedidoConfirmado ? (
              <ClienteForm onConfirm={handleConfirm} />
            ) : (
              <ClienteConfirm 
                pedidoData={pedidoConfirmado} 
                onNew={handleNewOrder}
                onVerSeguimiento={(token) => {
                  setSeguimientoToken(token);
                  window.history.pushState({}, '', `/seguimiento/${token}`);
                  setView('Seguimiento');
                }}
              />
            )}
          </section>
        )}

        {view === 'Seguimiento' && (
          <section id="viewSeguimiento" className="view active">
            <SeguimientoPedido token={seguimientoToken} onVolver={handleNewOrder} />
          </section>
        )}

        {view === 'Auth' && (
          <section className="view active">
            {authMode === 'login' && <Login onSwitchRegistro={()=>setAuthMode('registro')} onLoginSuccess={()=>setView('MiPanel')} />}
            {authMode === 'registro' && <Registro onSwitchLogin={()=>setAuthMode('login')} />}
            {authMode === 'verificar' && (
              <VerificarEmail 
                token={window.location.pathname.split('/')[2]} 
                onGoToLogin={()=>{
                  window.history.replaceState({}, '', '/');
                  setAuthMode('login');
                }}
              />
            )}
          </section>
        )}

        {view === 'MiPanel' && user && (
          <section className="view active">
            <PanelCliente />
          </section>
        )}

        {view === 'Negocio' && <NegocioPanel />}
      </main>
    </>
  );
}

function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}

export default App;
