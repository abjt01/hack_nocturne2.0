import React, { useState, useEffect } from 'react';
import API from '../services/api';
import './Audit.css';

const ACTION_META = {
  FHIR_BUNDLE_SERVED:  { icon: '📋', color: 'success', label: 'FHIR Bundle Served' },
  CONSENT_GRANTED:     { icon: '✅', color: 'success', label: 'Consent Granted' },
  ACCESS_DENIED:       { icon: '❌', color: 'error',   label: 'Access Denied' },
  CONSENT_REVOKED:     { icon: '⚠️', color: 'warning',  label: 'Consent Revoked' },
  PATIENT_REGISTERED:  { icon: '👤', color: 'info',    label: 'Patient Registered' },
};

export default function Audit({ backendUrl }) {
  const [events, setEvents]       = useState([]);
  const [loading, setLoading]     = useState(true);
  const [filter, setFilter]       = useState('all');
  const [verifying, setVerifying] = useState({});
  const [verifyResults, setVerifyResults] = useState({});

  useEffect(() => {
    let alive = true;
    const load = async () => {
      try {
        const res = await API.get('/api/audit/events');
        if (!alive) return;
        const data = res.data?.events || res.data || [];
        setEvents(data.map(e => ({
          id: e.event_id || e.id,
          action: e.event_type || e.action,
          requesting_hospital_id: e.actor_hospital_id || e.requesting_hospital_id,
          patient_global_id: e.subject_patient_id || e.patient_global_id,
          access_granted: e.outcome === 'SUCCESS' ? true : e.outcome === 'FAILURE' ? false : (e.access_granted ?? null),
          details: e.details || e.failure_reason || e.event_type || e.action,
          created_at: e.created_at || e.timestamp,
          hash: e.blockchain_hash || e.hash,
        })));
      } catch { }
      setLoading(false);
    };
    load();
    return () => { alive = false; };
  }, [backendUrl]);

  const verifyHash = async (eventId) => {
    setVerifying(v => ({ ...v, [eventId]: true }));
    try {
      const res = await API.get(`/api/audit/verify/${eventId}`);
      setVerifyResults(r => ({ ...r, [eventId]: { ok: res.data?.valid !== false, msg: res.data?.message || 'Hash verified ✓' } }));
    } catch {
      setVerifyResults(r => ({ ...r, [eventId]: { ok: false, msg: 'Verification failed — Service offline' } }));
    }
    setVerifying(v => ({ ...v, [eventId]: false }));
  };

  const filtered = events.filter(e => {
    if (filter === 'all')     return true;
    if (filter === 'granted') return e.access_granted === true;
    if (filter === 'denied')  return e.access_granted === false;
    return true;
  });

  const granted = events.filter(e => e.access_granted === true).length;
  const denied  = events.filter(e => e.access_granted === false).length;

  return (
    <div className="audit animate-fade-in">
      <div className="page-header">
        <h1>⛓️ Audit Trail</h1>
        <p>Tamper-proof SHA-256 cryptographic hash chain — every data access is immutably logged</p>
      </div>

      {/* Info Banner */}
      <div className="alert alert--info" style={{ marginBottom: 'var(--sp-5)' }}>
        🔒 <strong>Anti-Tamper Protection:</strong> Each audit event includes a SHA-256 hash computed from its contents.
        Clicking "Verify" checks the stored hash against a recomputed one to detect any tampering.
      </div>

      {/* Stats */}
      <div className="stats-grid" style={{ marginBottom: 'var(--sp-5)' }}>
        <div className="stat-card stat-card--blue animate-fade-up">
          <div className="stat-card__icon">📊</div>
          <div className="stat-card__body">
            <div className="stat-card__value">{events.length}</div>
            <div className="stat-card__label">Total Events</div>
          </div>
        </div>
        <div className="stat-card stat-card--green animate-fade-up">
          <div className="stat-card__icon">✅</div>
          <div className="stat-card__body">
            <div className="stat-card__value">{granted}</div>
            <div className="stat-card__label">Access Granted</div>
          </div>
        </div>
        <div className="stat-card stat-card--red animate-fade-up">
          <div className="stat-card__icon">❌</div>
          <div className="stat-card__body">
            <div className="stat-card__value">{denied}</div>
            <div className="stat-card__label">Access Denied</div>
          </div>
        </div>
      </div>

      {/* Filter */}
      <div className="audit__toolbar">
        {['all', 'granted', 'denied'].map(f => (
          <button
            key={f}
            className={`consent__filter-btn ${filter === f ? 'active' : ''}`}
            onClick={() => setFilter(f)}
          >
            {f === 'all' ? 'All Events' : f === 'granted' ? '✅ Granted' : '❌ Denied'}
          </button>
        ))}
      </div>

      {/* Events List */}
      {loading ? (
        <div className="page-loading"><span className="spinner" /> Loading audit trail...</div>
      ) : (
        <div className="audit__events">
          {filtered.map((e, idx) => {
            const meta = ACTION_META[e.action] || { icon: '•', color: 'gray', label: e.action };
            const vr   = verifyResults[e.id];
            return (
              <div
                key={e.id}
                className={`audit-event card animate-fade-up audit-event--${meta.color}`}
                style={{ animationDelay: `${idx * 0.04}s` }}
              >
                <div className="audit-event__header">
                  <div className="audit-event__left">
                    <span className="audit-event__icon">{meta.icon}</span>
                    <div>
                      <div className="audit-event__action">{meta.label}</div>
                      <div className="audit-event__time">
                        {e.created_at ? new Date(e.created_at).toLocaleString() : '—'}
                      </div>
                    </div>
                  </div>
                  <div className="audit-event__right">
                    {e.access_granted === true  && <span className="badge badge--success">✓ Granted</span>}
                    {e.access_granted === false && <span className="badge badge--error">✗ Denied</span>}
                  </div>
                </div>

                <div className="audit-event__body">
                  <div className="audit-event__detail">
                    <span className="audit-event__label">Hospital</span>
                    <span className="badge badge--blue">{e.requesting_hospital_id || '—'}</span>
                  </div>
                  <div className="audit-event__detail">
                    <span className="audit-event__label">Patient</span>
                    <code>{e.patient_global_id || '—'}</code>
                  </div>
                  <div className="audit-event__detail">
                    <span className="audit-event__label">Details</span>
                    <span>{e.details || '—'}</span>
                  </div>
                  <div className="audit-event__detail audit-event__hash-row">
                    <span className="audit-event__label">SHA-256 Hash</span>
                    <code className="audit-event__hash">{e.blockchain_hash || e.hash || '—'}</code>
                    <button
                      className={`btn btn--sm ${vr ? (vr.ok ? 'btn--secondary' : 'btn--danger') : 'btn--secondary'}`}
                      onClick={() => verifyHash(e.id)}
                      disabled={verifying[e.id]}
                    >
                      {verifying[e.id]
                        ? <><span className="spinner spinner--sm" /> Verifying...</>
                        : vr
                          ? (vr.ok ? '✓ Verified' : '✗ Tampered!')
                          : '🔍 Verify'}
                    </button>
                  </div>
                  {vr && (
                    <div className={`alert alert--${vr.ok ? 'success' : 'error'}`} style={{ margin: 0 }}>
                      {vr.ok ? '✅' : '🚨'} {vr.msg}
                    </div>
                  )}
                </div>
              </div>
            );
          })}
          {filtered.length === 0 && (
            <div className="empty-state">
              <span className="empty-state__icon">⛓️</span>
              <span className="empty-state__text">No events match this filter</span>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
