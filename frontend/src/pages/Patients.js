import React, { useState, useEffect } from 'react';
import API from '../services/api';
import './Patients.css';

function age(dob) {
  if (!dob) return '—';
  return Math.floor((Date.now() - new Date(dob)) / (365.25 * 24 * 3600 * 1000));
}

export default function Patients({ backendUrl }) {
  const [patients, setPatients] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [hospFilter, setHospFilter] = useState('all');
  const [expanded, setExpanded] = useState(null);

  useEffect(() => {
    let alive = true;
    const load = async () => {
      try {
        const res = await API.get('/api/patients');
        if (!alive) return;
        const data = res.data?.patients || res.data || [];
        setPatients(data.map(p => ({
          ...p,
          name: p.name || `${p.given_name || p.first_name || ''} ${p.family_name || p.last_name || ''}`.trim(),
          dob: p.dob || p.birth_date || p.date_of_birth,
          id: p.global_id || p.id,
          local_id: p.local_patient_id || p.local_id,
          hospital_id: p.hospital_id,
        })));
      } catch { }
      setLoading(false);
    };
    load();
    return () => { alive = false; };
  }, [backendUrl]);

  const filtered = patients.filter(p => {
    const matchSearch = !search || p.name?.toLowerCase().includes(search.toLowerCase()) || p.id?.toLowerCase().includes(search.toLowerCase());
    const matchHosp = hospFilter === 'all' || p.hospital_id === hospFilter;
    return matchSearch && matchHosp;
  });

  const hospitals = [...new Set(patients.map(p => p.hospital_id))];

  return (
    <div className="patients animate-fade-in">
      <div className="page-header">
        <h1>👤 Patient Records</h1>
        <p>Global patient registry with cross-hospital identity resolution</p>
      </div>

      {/* Toolbar */}
      <div className="patients__toolbar">
        <div className="search-bar">
          <span className="search-bar__icon">🔍</span>
          <input className="form-control" placeholder="Search by name or ID..." value={search} onChange={e => setSearch(e.target.value)} />
        </div>
        <select className="form-control" style={{ width: 200 }} value={hospFilter} onChange={e => setHospFilter(e.target.value)}>
          <option value="all">All Hospitals</option>
          {hospitals.map(h => <option key={h} value={h}>{h}</option>)}
        </select>
        <div style={{ color: 'var(--gray-500)', fontSize: 'var(--text-sm)', fontWeight: 500 }}>
          {filtered.length} patient{filtered.length !== 1 ? 's' : ''}
        </div>
      </div>

      {loading ? (
        <div className="page-loading"><span className="spinner" /> Loading patients...</div>
      ) : (
        <div className="card">
          <div className="table-wrap">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Global ID</th>
                  <th>Name</th>
                  <th>Age / DOB</th>
                  <th>Gender</th>
                  <th>Hospital</th>
                  <th>Blood Type</th>
                  <th>Diagnoses</th>
                </tr>
              </thead>
              <tbody>
                {filtered.length === 0 ? (
                  <tr><td colSpan={7} style={{ textAlign: 'center', color: 'var(--gray-400)', padding: 32 }}>No patients found</td></tr>
                ) : filtered.map(p => (
                  <React.Fragment key={p.id}>
                    <tr
                      className={`patients__row ${expanded === p.id ? 'patients__row--expanded' : ''}`}
                      onClick={() => setExpanded(expanded === p.id ? null : p.id)}
                      style={{ cursor: 'pointer' }}
                    >
                      <td><code>{p.id}</code></td>
                      <td>
                        <div className="patients__name">
                          <div className="patients__avatar">{(p.name || '?').charAt(0)}</div>
                          <span style={{ fontWeight: 600 }}>{p.name || '—'}</span>
                        </div>
                      </td>
                      <td>
                        <div style={{ fontWeight: 600 }}>{age(p.dob)} yrs</div>
                        <div style={{ fontSize: 'var(--text-xs)', color: 'var(--gray-400)' }}>{p.dob}</div>
                      </td>
                      <td>
                        <span className={`badge ${p.gender === 'female' ? 'badge--info' : 'badge--gray'}`}>
                          {p.gender === 'female' ? '♀' : '♂'} {p.gender || '—'}
                        </span>
                      </td>
                      <td>
                        <span className="badge badge--blue">{p.hospital_id || '—'}</span>
                      </td>
                      <td>
                        <span className="badge badge--error">{p.blood_type || '—'}</span>
                      </td>
                      <td>
                        <div className="patients__diagnoses">
                          {(p.diagnoses || []).map(d => (
                            <span key={d} className="badge badge--warning">{d}</span>
                          ))}
                        </div>
                      </td>
                    </tr>
                    {expanded === p.id && (
                      <tr className="patients__detail-row">
                        <td colSpan={7}>
                          <div className="patients__detail">
                            <div className="patients__detail-grid">
                              <div>
                                <div className="patients__detail-label">Local Hospital ID</div>
                                <code>{p.local_id || '—'}</code>
                              </div>
                              <div>
                                <div className="patients__detail-label">Global UUID</div>
                                <code>{p.id}</code>
                              </div>
                              <div>
                                <div className="patients__detail-label">Primary Hospital</div>
                                <strong>{p.hospital_id}</strong>
                              </div>
                              <div>
                                <div className="patients__detail-label">Date of Birth</div>
                                <span>{p.dob ? new Date(p.dob).toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' }) : '—'}</span>
                              </div>
                            </div>
                          </div>
                        </td>
                      </tr>
                    )}
                  </React.Fragment>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
