import React, { useState, useEffect } from 'react';
import {
  LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, Legend, PieChart, Pie, Cell
} from 'recharts';
import API from '../services/api';
import './Dashboard.css';

const COLORS = ['#2563eb', '#0ea5e9', '#14b8a6', '#8b5cf6'];

function StatCard({ icon, label, value, sub, color = 'blue', trend }) {
  return (
    <div className={`stat-card stat-card--${color} animate-fade-up`}>
      <div className="stat-card__icon">{icon}</div>
      <div className="stat-card__body">
        <div className="stat-card__value">{value}</div>
        <div className="stat-card__label">{label}</div>
        {sub && <div className="stat-card__sub">{sub}</div>}
      </div>
      {trend !== undefined && (
        <div className={`stat-card__trend ${trend >= 0 ? 'up' : 'down'}`}>
          {trend >= 0 ? '↑' : '↓'} {Math.abs(trend)}%
        </div>
      )}
    </div>
  );
}

function CustomTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null;
  return (
    <div className="chart-tooltip">
      <div className="chart-tooltip__label">{label}</div>
      {payload.map((p, i) => (
        <div key={i} className="chart-tooltip__item" style={{ color: p.color }}>
          {p.name}: <strong>{p.value}</strong>
        </div>
      ))}
    </div>
  );
}

// Initial values for dashboard
const DEFAULT_STATS = {
  hospitals: 0,
  patients: 0,
  active_consents: 0,
  total_audits: 0,
  fhir_requests: 0,
  access_denied: 0,
};

export default function Dashboard({ backendUrl }) {
  const [stats, setStats] = useState(DEFAULT_STATS);
  const [feed, setFeed] = useState([]);
  const [connected, setConnected] = useState(null);

  useEffect(() => {
    let alive = true;
    const load = async () => {
      try {
        const res = await API.get('/api/health');
        if (!alive) return;
        if (res.data?.status === 'healthy') {
          setConnected(true);
          // Load real stats
          const [hRes, pRes, aRes] = await Promise.allSettled([
            API.get('/api/hospitals'),
            API.get('/api/patients'),
            API.get('/api/audit/events'),
          ]);
          
          const hospitals = hRes.status === 'fulfilled' ? (hRes.value.data?.hospitals || hRes.value.data || []).length : 0;
          const patientsList = pRes.status === 'fulfilled' ? (pRes.value.data?.patients || pRes.value.data || []) : [];
          const patients = patientsList.length;

          let consentsCount = 0;
          try {
            const limit = patientsList.slice(0, 5);
            if (limit.length > 0) {
              let count = 0;
              for (const p of limit) {
                const c = await API.get(`/api/consent/${p.global_id || p.id}`).catch(() => ({ data: { consents: [] } }));
                count += (c.data?.consents || []).length;
              }
              consentsCount = count;
            }
          } catch (e) { }

          const audits = aRes.status === 'fulfilled' ? (aRes.value.data?.events || aRes.value.data || []).length : 0;
          setStats({ hospitals, patients, active_consents: consentsCount, total_audits: audits, fhir_requests: 0, access_denied: 0 });

          if (aRes.status === 'fulfilled') {
            const raw = aRes.value.data?.events || aRes.value.data || [];
            setFeed(raw.slice(0, 6).map((e, i) => ({
              id: i, time: new Date(e.created_at || Date.now()).toLocaleTimeString(),
              type: e.action || 'EVENT', actor: e.requesting_hospital_id || '—',
              patient: e.patient_global_id || '—', status: e.access_granted !== false ? 'success' : 'error',
              msg: e.details || e.action,
            })));
          }
        } else {
            setConnected(false);
        }
      } catch {
        setConnected(false);
      }
    };
    load();
    return () => { alive = false; };
  }, [backendUrl]);

  const statusIcon = { success: '✅', error: '❌', warning: '⚠️' };

  return (
    <div className="dashboard animate-fade-in">
      <div className="page-header">
        <h1>📊 Dashboard</h1>
        <p>Vital — FHIR Healthcare Interoperability Platform — Real-time overview</p>
        {connected === false && (
          <div className="alert alert--warning" style={{ marginTop: 12 }}>
            ⚠️ Backend unreachable. Ensure the platform is running with <code>docker compose up</code>
          </div>
        )}
      </div>

      {/* Stats */}
      <div className="stats-grid">
        <StatCard icon="🏥" label="Hospitals" value={stats.hospitals} sub="Registered institutions" color="blue" />
        <StatCard icon="👤" label="Patients" value={stats.patients} sub="Global identities" color="teal" />
        <StatCard icon="🔐" label="Active Consents" value={stats.active_consents} sub="Cross-hospital grants" color="green" />
        <StatCard icon="⛓️" label="Audit Events" value={stats.total_audits} sub="Tamper-proof records" color="purple" />
        <StatCard icon="📋" label="FHIR Requests" value={stats.fhir_requests} sub="Bundle fetches" color="sky" />
        <StatCard icon="🚫" label="Access Denied" value={stats.access_denied} sub="Consent violations" color="red" />
      </div>

      {/* Charts Row */}
      <div className="content-grid" style={{ marginBottom: 'var(--sp-5)' }}>
        {/* Activity Chart */}
        <div className="card animate-fade-up" style={{ animationDelay: '0.1s' }}>
          <div className="card__header">
            <div className="card__title">
              <div className="card__icon">📈</div>
              API Activity
            </div>
          </div>
          <div className="card__body">
            <ResponsiveContainer width="100%" height={220}>
              <LineChart data={[]} margin={{ top: 5, right: 10, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
                <XAxis dataKey="time" tick={{ fontSize: 11, fill: '#64748b' }} stroke="rgba(255,255,255,0.06)" />
                <YAxis tick={{ fontSize: 11, fill: '#64748b' }} stroke="rgba(255,255,255,0.06)" />
                <Tooltip content={<CustomTooltip />} />
                <Legend wrapperStyle={{ fontSize: 12, color: '#94a3b8' }} />
                <Line type="monotone" dataKey="requests" name="Requests" stroke="#2563eb" strokeWidth={2} dot={false} activeDot={{ r: 5 }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Hospital Distribution */}
        <div className="card animate-fade-up" style={{ animationDelay: '0.15s' }}>
          <div className="card__header">
            <div className="card__title">
              <div className="card__icon">🏥</div>
              Patient Distribution
            </div>
          </div>
          <div className="card__body dashboard__pie-wrap">
            <ResponsiveContainer width="100%" height={220}>
              <PieChart>
                <Pie
                  data={[]}
                  cx="50%" cy="50%"
                  innerRadius={55} outerRadius={85}
                  paddingAngle={4}
                  dataKey="value"
                  nameKey="name"
                  labelLine={false}
                >
                  <Cell fill={COLORS[0]} />
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Bar Chart + Feed */}
      <div className="content-grid">
        <div className="card animate-fade-up" style={{ animationDelay: '0.2s' }}>
          <div className="card__header">
            <div className="card__title">
              <div className="card__icon">📊</div>
              Hourly FHIR Requests
            </div>
          </div>
          <div className="card__body">
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={[]} margin={{ top: 5, right: 10, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
                <XAxis dataKey="time" tick={{ fontSize: 11, fill: '#64748b' }} stroke="rgba(255,255,255,0.06)" />
                <YAxis tick={{ fontSize: 11, fill: '#64748b' }} stroke="rgba(255,255,255,0.06)" />
                <Tooltip content={<CustomTooltip />} />
                <Bar dataKey="requests" name="Requests" fill="#2563eb" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Live Audit Feed */}
        <div className="card animate-fade-up" style={{ animationDelay: '0.25s' }}>
          <div className="card__header">
            <div className="card__title">
              <div className="card__icon">📡</div>
              Live Audit Feed
            </div>
            <span className="dashboard__live-badge">
              <span className="dashboard__live-dot" /> LIVE
            </span>
          </div>
          <div className="card__body dashboard__feed">
            {feed.map(item => (
              <div key={item.id} className={`dashboard__feed-item dashboard__feed-item--${item.status}`}>
                <div className="dashboard__feed-top">
                  <span className="dashboard__feed-icon">{statusIcon[item.status] || '•'}</span>
                  <span className="dashboard__feed-type">{item.type.replace(/_/g, ' ')}</span>
                  <span className="dashboard__feed-time">{item.time}</span>
                </div>
                <div className="dashboard__feed-msg">{item.msg}</div>
                {item.patient !== '—' && (
                  <div className="dashboard__feed-meta">Patient: <code>{item.patient}</code> · Actor: <code>{item.actor}</code></div>
                )}
              </div>
            ))}
            {feed.length === 0 && <div style={{ textAlign: 'center', color: 'var(--gray-400)', padding: 20 }}>No audit events yet</div>}
          </div>
        </div>
      </div>

      {/* Services Status */}
      <div className="card animate-fade-up" style={{ marginTop: 'var(--sp-5)', animationDelay: '0.3s' }}>
        <div className="card__header">
          <div className="card__title">
            <div className="card__icon">🔧</div>
            Microservices Status
          </div>
        </div>
        <div className="card__body dashboard__services">
          {[
            { name: 'Hospital Registry', icon: '🏥', status: connected ? 'up' : 'down' },
            { name: 'Master Patient Index', icon: '🔍', status: connected ? 'up' : 'down' },
            { name: 'Patient Data Service', icon: '👤', status: connected ? 'up' : 'down' },
            { name: 'Consent Service', icon: '🔐', status: connected ? 'up' : 'down' },
            { name: 'FHIR Bundle Service', icon: '📋', status: connected ? 'up' : 'down' },
            { name: 'Audit / Anti-Tamper', icon: '⛓️', status: connected ? 'up' : 'down' },
          ].map(svc => (
            <div key={svc.name} className="dashboard__service-card">
              <div className="dashboard__service-icon">{svc.icon}</div>
              <div className="dashboard__service-name">{svc.name}</div>
              <span className={`badge badge--${svc.status === 'up' ? 'success' : 'error'}`}>
                {svc.status === 'up' ? '✓ Online' : '✗ Down'}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
