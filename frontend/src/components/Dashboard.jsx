import { useState, useEffect } from 'react';
import { apiFetch } from '../utils';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';

function Dashboard() {
  const [stats, setStats] = useState(null);
  const [periodo, setPeriodo] = useState('hoy'); // hoy | semana | mes | todos

  useEffect(() => {
    async function fetchStats() {
      try {
        const res = await apiFetch(`/api/stats?periodo=${periodo}`);
        const data = await res.json();
        setStats(data);
      } catch (err) {
        console.error("Error fetching stats:", err);
      }
    }
    fetchStats();
  }, [periodo]);

  if (!stats) return <div style={{padding:20}}>Cargando dashboard...</div>;

  const fmt = (n) => '$' + n.toLocaleString('es-AR');
  const kpiStyle = { background: 'var(--paper)', border: '1px solid var(--line)', borderRadius: 6, padding: 16, flex: '1 1 150px' };
  const numStyle = { fontSize: 24, fontWeight: 'bold', color: 'var(--text)', marginTop: 8 };
  const labelStyle = { fontSize: 12, color: 'var(--text-dim)', textTransform: 'uppercase', letterSpacing: '.05em' };

  const COLORS = ['#8A93A6', '#185FA5', '#854F0B', '#3B6D11', '#4A1B0C'];

  return (
    <div style={{paddingBottom: 40}}>
      <div style={{display:'flex', justifyContent:'space-between', alignItems:'center', marginBottom: 20}}>
        <h2 className="section" style={{margin:0}}>Métricas</h2>
        <select value={periodo} onChange={e=>setPeriodo(e.target.value)} style={{padding: '4px 8px', borderRadius: 4, border: '1px solid var(--line)'}}>
          <option value="hoy">Hoy</option>
          <option value="semana">Esta semana</option>
          <option value="mes">Este mes</option>
          <option value="todos">Histórico completo</option>
        </select>
      </div>

      <div style={{display:'flex', flexWrap:'wrap', gap: 12, marginBottom: 24}}>
        <div style={kpiStyle}>
          <div style={labelStyle}>Facturación Estimada</div>
          <div style={{...numStyle, color: 'var(--stamp)'}}>{fmt(stats.kpis.facturacion)}</div>
        </div>
        <div style={kpiStyle}>
          <div style={labelStyle}>Archivos Impresos</div>
          <div style={numStyle}>{stats.kpis.impresos}</div>
        </div>
        <div style={kpiStyle}>
          <div style={labelStyle}>Pedidos Pendientes</div>
          <div style={numStyle}>{stats.kpis.pendientes}</div>
        </div>
      </div>

      <div className="grid2">
        <div style={{...kpiStyle, padding: 20}}>
          <h3 style={{fontSize: 14, margin: '0 0 16px', color: 'var(--text)'}}>Pedidos por Estado</h3>
          <div style={{height: 250}}>
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={stats.charts.estados} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={80} label>
                  {stats.charts.estados.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div style={{...kpiStyle, padding: 20}}>
          <h3 style={{fontSize: 14, margin: '0 0 16px', color: 'var(--text)'}}>Facturación por Sucursal</h3>
          <div style={{height: 250}}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={stats.charts.sucursales}>
                <XAxis dataKey="name" tick={{fontSize: 11}} />
                <YAxis tick={{fontSize: 11}} />
                <Tooltip formatter={(val) => fmt(val)} />
                <Bar dataKey="facturacion" fill="var(--stamp)" radius={[4,4,0,0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      <div style={{...kpiStyle, marginTop: 14, padding: 20}}>
        <h3 style={{fontSize: 14, margin: '0 0 16px', color: 'var(--text)'}}>Páginas Impresas (B/N vs Color)</h3>
        <div style={{display:'flex', gap: 40}}>
          <div>
            <div style={labelStyle}>Blanco y Negro</div>
            <div style={numStyle}>{stats.kpis.paginas_bn} pág.</div>
          </div>
          <div>
            <div style={labelStyle}>Color</div>
            <div style={numStyle}>{stats.kpis.paginas_color} pág.</div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;
