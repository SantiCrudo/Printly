import { useState, useEffect } from 'react';
import { apiFetch } from '../utils';
import { useAuth } from '../context/AuthContext';
import { Turnstile } from '@marsidev/react-turnstile';

function ClienteForm({ onConfirm }) {
  const { user, token } = useAuth();

  const [nombre, setNombre] = useState('');
  const [contacto, setContacto] = useState('');
  const [desc, setDesc] = useState('');
  const [archivo, setArchivo] = useState(null);
  const [copias, setCopias] = useState(1);
  const [paginas, setPaginas] = useState(1);
  const [color, setColor] = useState(false);
  const [dobleFaz, setDobleFaz] = useState(false);
  const [tamano, setTamano] = useState('A4');

  const [sucursales, setSucursales] = useState([]);
  const [sucursalId, setSucursalId] = useState('');
  const [precios, setPrecios] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [turnstileToken, setTurnstileToken] = useState(null);

  useEffect(() => {
    async function fetchTenantInfo() {
      try {
        const res = await apiFetch('/api/tenant/info');
        const data = await res.json();
        setSucursales(data.sucursales || []);
        if (data.sucursales && data.sucursales.length > 0) {
          setSucursalId(data.sucursales[0].id);
        }
        setPrecios(data.precios);
      } catch (err) {
        console.error("Error fetching tenant info:", err);
      }
    }
    fetchTenantInfo();
  }, []);

  const calcPrecio = () => {
    if (!precios) return 0;
    const base = color ? precios.precio_color_pagina : precios.precio_bn_pagina;
    const recargo = tamano === 'A3' ? precios.recargo_a3 : (tamano === 'Oficio' ? precios.recargo_oficio : 1);
    return Math.round(base * recargo * paginas * copias);
  };

  const fmt = (n) => '$' + n.toLocaleString('es-AR');

  const handleSubmit = async () => {
    if (!archivo) {
      alert('Subí un archivo para continuar.');
      return;
    }
    if (!sucursalId) {
      alert('Seleccioná una sucursal.');
      return;
    }
    if (!user && !turnstileToken) {
      alert('Por favor completá la validación de seguridad.');
      return;
    }

    setIsSubmitting(true);

    const formData = new FormData();
    formData.append('desc', desc);
    formData.append('copias', copias);
    formData.append('paginas', paginas);
    formData.append('color', color);
    formData.append('doble_faz', dobleFaz);
    formData.append('tamano', tamano);
    formData.append('sucursal_id', sucursalId);
    formData.append('archivo', archivo);

    if (!user) {
      formData.append('nombre', nombre || 'Cliente sin nombre');
      formData.append('contacto', contacto);
      formData.append('turnstile_token', turnstileToken);
    }

    const endpoint = user ? '/api/pedidos/registrado' : '/api/pedidos/invitado';
    const headers = {};
    if (token) headers['Authorization'] = `Bearer ${token}`;

    try {
      const res = await apiFetch(endpoint, {
        method: 'POST',
        headers,
        body: formData,
      });
      if (!res.ok) throw new Error('Error al enviar el pedido');
      const data = await res.json();
      onConfirm(data);
    } catch (err) {
      alert(err.message);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div id="clienteForm">
      <h2 className="section">{user ? 'Subir nuevo trabajo' : 'Subí tu trabajo — sin registro'}</h2>
      <div className="form-card">

        {sucursales.length > 1 && (
          <div className="field">
            <label>Sucursal de retiro</label>
            <select value={sucursalId} onChange={e => setSucursalId(e.target.value)}>
              {sucursales.map(s => (
                <option key={s.id} value={s.id}>{s.nombre} - {s.direccion}</option>
              ))}
            </select>
          </div>
        )}

        {!user && (
          <div className="grid2">
            <div className="field">
              <label>Nombre</label>
              <input type="text" placeholder="Tu nombre" value={nombre} onChange={e => setNombre(e.target.value)} />
            </div>
            <div className="field">
              <label>Mail o teléfono</label>
              <input type="text" placeholder="Opcional, uno de los dos" value={contacto} onChange={e => setContacto(e.target.value)} />
            </div>
          </div>
        )}

        <div className="field">
          <label>Archivo</label>
          <input type="file" accept=".pdf,.jpg,.jpeg,.png,.docx" onChange={e => setArchivo(e.target.files[0])} />
        </div>

        <div className="field">
          <label>Descripción del trabajo</label>
          <textarea placeholder="Ej: 2 juegos, doble faz, de pág 3 a la 10" value={desc} onChange={e => setDesc(e.target.value)} />
        </div>

        <div className="grid2">
          <div className="field">
            <label>Copias / juegos</label>
            <input type="number" min="1" value={copias} onChange={e => setCopias(parseInt(e.target.value) || 1)} />
          </div>
          <div className="field">
            <label>Páginas a imprimir</label>
            <input type="number" min="1" value={paginas} onChange={e => setPaginas(parseInt(e.target.value) || 1)} />
          </div>
        </div>

        <div className="field">
          <label>Opciones</label>
          <div className="toggle-row">
            <label><input type="checkbox" checked={color} onChange={e => setColor(e.target.checked)} /> Color</label>
            <label><input type="checkbox" checked={dobleFaz} onChange={e => setDobleFaz(e.target.checked)} /> Doble faz</label>
            <select style={{ width: 'auto' }} value={tamano} onChange={e => setTamano(e.target.value)}>
              <option value="A4">A4</option>
              {precios?.recargo_a3 > 1 && <option value="A3">A3</option>}
              {precios?.recargo_oficio > 1 && <option value="Oficio">Oficio</option>}
            </select>
          </div>
        </div>

        <div className="price-line">
          <span>Precio estimado</span>
          <span className="amt">{fmt(calcPrecio())}</span>
        </div>
        <p className="hint">Se paga en el local al retirar. Esto es solo una estimación.</p>

        {!user && (
          <div style={{ marginTop: 16 }}>
            <Turnstile siteKey="1x00000000000000000000AA" onSuccess={(token) => setTurnstileToken(token)} />
          </div>
        )}

        <div style={{ marginTop: 16 }}>
          <button className="btn stamp" onClick={handleSubmit} disabled={isSubmitting || !precios || (!user && !turnstileToken)}>
            {isSubmitting ? 'Enviando...' : 'Confirmar pedido'}
          </button>
        </div>
      </div>
    </div>
  );
}

export default ClienteForm;
