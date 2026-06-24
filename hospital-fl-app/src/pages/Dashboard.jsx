import React, { useState, useEffect, useCallback, useRef } from 'react';
import { Activity, Database, Server, UserPlus, FileHeart, LogOut, ShieldCheck, CheckSquare2, RefreshCw, FileText, X } from 'lucide-react';
import Report from './Report';

// ── Disease definitions ────────────────────────────────────────────────────
const DISEASE_SCHEMAS = {
  heart: {
    label: 'Heart Disease Risk',
    color: '#ef4444',
    fields: [
      { key: 'age',      label: 'Age',                type: 'number', placeholder: 'e.g. 45' },
      { key: 'sex',      label: 'Gender',              type: 'select', options: [{ v:'0',l:'Female' },{ v:'1',l:'Male' }] },
      { key: 'cp',       label: 'Chest Pain Type',     type: 'select', options: [{ v:'0',l:'Typical Angina' },{ v:'1',l:'Atypical Angina' },{ v:'2',l:'Non-anginal Pain' },{ v:'3',l:'Asymptomatic' }] },
      { key: 'trestbps', label: 'Resting BP (mmHg)',   type: 'number', placeholder: 'e.g. 120' },
      { key: 'chol',     label: 'Cholesterol (mg/dl)', type: 'number', placeholder: 'e.g. 210' },
      { key: 'fbs',      label: 'Fasting BS >120',     type: 'select', options: [{ v:'0',l:'No' },{ v:'1',l:'Yes' }] },
      { key: 'restecg',  label: 'Resting ECG',         type: 'select', options: [{ v:'0',l:'Normal' },{ v:'1',l:'ST-T Wave Abnormality' },{ v:'2',l:'Left Ventricular Hypertrophy' }] },
      { key: 'thalach',  label: 'Max Heart Rate',      type: 'number', placeholder: 'e.g. 150' },
      { key: 'exang',    label: 'Exercise Angina',     type: 'select', options: [{ v:'0',l:'No' },{ v:'1',l:'Yes' }] },
      { key: 'oldpeak',  label: 'ST Depression',       type: 'number', step: '0.1', placeholder: 'e.g. 1.2' },
      { key: 'slope',    label: 'ST Slope',            type: 'select', options: [{ v:'0',l:'Upsloping' },{ v:'1',l:'Flat' },{ v:'2',l:'Downsloping' }] },
      { key: 'ca',       label: 'Major Vessels (0-3)', type: 'select', options: [{ v:'0',l:'0' },{ v:'1',l:'1' },{ v:'2',l:'2' },{ v:'3',l:'3' }] },
      { key: 'thal',     label: 'Thalassemia',         type: 'select', options: [{ v:'3',l:'Normal' },{ v:'6',l:'Fixed Defect' },{ v:'7',l:'Reversible Defect' }] },
    ],
    tableHeaders: ['Age','Gender','Chest Pain','Resting BP','Cholesterol','FBS','ECG','Max HR','Ex Angina','ST Dep','Slope','Vessels','Thal'],
    tableKeys:    ['age','sex','cp','trestbps','chol','fbs','restecg','thalach','exang','oldpeak','slope','ca','thal'],
  },
  cancer: {
    label: 'Cancer Risk Profile',
    color: '#f59e0b',
    fields: [
      { key: 'Age',                  label: 'Age',                    type: 'number', placeholder: 'e.g. 45' },
      { key: 'Gender',               label: 'Gender',                 type: 'select', options: [{ v:'0',l:'Female' },{ v:'1',l:'Male' }] },
      { key: 'Air Pollution',        label: 'Air Pollution (1-9)',     type: 'number', min:1, max:9, placeholder: '1-9' },
      { key: 'Alcohol use',          label: 'Alcohol Use (1-9)',       type: 'number', min:1, max:9, placeholder: '1-9' },
      { key: 'Dust Allergy',         label: 'Dust Allergy (1-9)',      type: 'number', min:1, max:9, placeholder: '1-9' },
      { key: 'OccuPational Hazards', label: 'Occupational Hazards',   type: 'number', min:1, max:9, placeholder: '1-9' },
      { key: 'Genetic Risk',         label: 'Genetic Risk (1-9)',      type: 'number', min:1, max:9, placeholder: '1-9' },
      { key: 'Chronic Lung Disease', label: 'Chronic Lung Disease',   type: 'select', options: [{ v:'0',l:'No' },{ v:'1',l:'Yes' }] },
      { key: 'Balanced Diet',        label: 'Balanced Diet (1-9)',     type: 'number', min:1, max:9, placeholder: '1-9' },
      { key: 'Obesity',              label: 'Obesity',                type: 'select', options: [{ v:'0',l:'No' },{ v:'1',l:'Yes' }] },
      { key: 'Smoking',              label: 'Smoking',                type: 'select', options: [{ v:'0',l:'No' },{ v:'1',l:'Yes' }] },
      { key: 'Passive Smoker',       label: 'Passive Smoker',         type: 'select', options: [{ v:'0',l:'No' },{ v:'1',l:'Yes' }] },
      { key: 'Chest Pain',           label: 'Chest Pain',             type: 'select', options: [{ v:'0',l:'No' },{ v:'1',l:'Yes' }] },
      { key: 'Coughing of Blood',   label: 'Coughing of Blood',      type: 'select', options: [{ v:'0',l:'No' },{ v:'1',l:'Yes' }] },
      { key: 'Fatigue',             label: 'Fatigue',                type: 'select', options: [{ v:'0',l:'No' },{ v:'1',l:'Yes' }] },
      { key: 'Weight Loss',         label: 'Weight Loss',            type: 'select', options: [{ v:'0',l:'No' },{ v:'1',l:'Yes' }] },
      { key: 'Shortness of Breath', label: 'Shortness of Breath',      type: 'select', options: [{ v:'0',l:'No' },{ v:'1',l:'Yes' }] },
      { key: 'Wheezing',            label: 'Wheezing',               type: 'select', options: [{ v:'0',l:'No' },{ v:'1',l:'Yes' }] },
      { key: 'Swallowing Difficulty', label: 'Swallowing Difficulty',  type: 'select', options: [{ v:'0',l:'No' },{ v:'1',l:'Yes' }] },
      { key: 'Clubbing of Finger Nails', label: 'Clubbing of Nails',   type: 'select', options: [{ v:'0',l:'No' },{ v:'1',l:'Yes' }] },
      { key: 'Frequent Cold',       label: 'Frequent Cold',          type: 'select', options: [{ v:'0',l:'No' },{ v:'1',l:'Yes' }] },
      { key: 'Dry Cough',           label: 'Dry Cough',              type: 'select', options: [{ v:'0',l:'No' },{ v:'1',l:'Yes' }] },
      { key: 'Snoring',             label: 'Snoring',                type: 'select', options: [{ v:'0',l:'No' },{ v:'1',l:'Yes' }] },
    ],
    tableHeaders: ['Age','Gender','Air Pollution','Alcohol Use','Dust Allergy','Occ. Hazards','Genetic Risk','Lung Disease','Balanced Diet','Obesity','Smoking','Passive Smoker','Chest Pain','Cough Blood','Fatigue','Wt Loss','Breath','Wheeze','Swallow','Nails','Cold','Cough','Snore'],
    tableKeys:    ['Age','Gender','Air Pollution','Alcohol use','Dust Allergy','OccuPational Hazards','Genetic Risk','Chronic Lung Disease','Balanced Diet','Obesity','Smoking','Passive Smoker','Chest Pain','Coughing of Blood','Fatigue','Weight Loss','Shortness of Breath','Wheezing','Swallowing Difficulty','Clubbing of Finger Nails','Frequent Cold','Dry Cough','Snoring'],
  },
  anaemia: {
    label: 'Anaemia Risk Context',
    color: '#8b5cf6',
    fields: [
      { key: 'Sex',         label: 'Gender',              type: 'select', options: [{ v:'0',l:'Female' },{ v:'1',l:'Male' }] },
      { key: '%Red Pixel',  label: '% Red Pixel',         type: 'number', step: '0.1', placeholder: 'e.g. 32.8' },
      { key: '%Green Pixel',label: '% Green Pixel',       type: 'number', step: '0.1', placeholder: 'e.g. 47.0' },
      { key: '%Blue Pixel', label: '% Blue Pixel',        type: 'number', step: '0.1', placeholder: 'e.g. 20.2' },
      { key: 'Hb',          label: 'Haemoglobin (g/dl)', type: 'number', step: '0.1', placeholder: 'e.g. 9.8' },
    ],
    tableHeaders: ['Gender','% Red Pixel','% Green Pixel','% Blue Pixel','Haemoglobin (Hb)'],
    tableKeys:    ['Sex','%Red Pixel','%Green Pixel','%Blue Pixel','Hb'],
  },
};

const DISEASE_LIST = Object.keys(DISEASE_SCHEMAS);

function buildEmptyForm(disease) {
  const schema = DISEASE_SCHEMAS[disease] || DISEASE_SCHEMAS.heart;
  return schema.fields.reduce((acc, f) => { acc[f.key] = ''; return acc; }, {});
}

// ── Specialist Mapping ───────────────────────────────────────────────────
const SPECIALIZATION_TO_DISEASE = {
  'Cardiology': 'heart',
  'Oncology': 'cancer',
  'Haematology': 'anaemia'
};

// ── Main Dashboard ─────────────────────────────────────────────────────────
export default function Dashboard({ hospital, onLogout }) {
  const [patients, setPatients] = useState([]);
  const [dbLoading, setDbLoading] = useState(false);
  const [dbError, setDbError] = useState(null);
  const [adminDateFilter, setAdminDateFilter] = useState('');
  
  // Doctors only see their specialization, admins see 'all' by default
  const initialDiseaseFilter = hospital?.role === 'doctor' && hospital?.specialization
    ? SPECIALIZATION_TO_DISEASE[hospital.specialization] || 'all'
    : 'all';
    
  const [dbDiseaseFilter, setDbDiseaseFilter] = useState(initialDiseaseFilter);

  const [currentView, setCurrentView] = useState(hospital?.role === 'doctor' ? 'database' : 'predict');
  const [selectedDisease, setSelectedDisease] = useState('heart');
  const [formData, setFormData] = useState(buildEmptyForm('heart'));

  const [predictionStatus, setPredictionStatus] = useState('idle');
  const [predictionResult, setPredictionResult] = useState('');

  const [flStatus, setFlStatus] = useState('idle');
  const [flErrorMessage, setFlErrorMessage] = useState(null);
  const suppressFlErrorRef = useRef(false);
  const lastApiTrainingStatusRef = useRef(null);
  const completeDismissTimerRef = useRef(null);

  const [showReport, setShowReport] = useState(false);
  const [reportData, setReportData] = useState(null);

  // When disease selection changes, reset form
  const handleDiseaseChange = (newDisease) => {
    setSelectedDisease(newDisease);
    setFormData(buildEmptyForm(newDisease));
    setPredictionStatus('idle');
    setPredictionResult('');
  };

  const loadRecords = useCallback(async (options = {}) => {
    const { silent = false } = options;
    if (!hospital?.id) return;
    if (!silent) { setDbLoading(true); setDbError(null); }
    try {
      let url = `http://127.0.0.1:8000/records?hospital_id=${encodeURIComponent(hospital.id)}`;
      if (hospital?.role === 'doctor') {
        url += `&doctor_id=${encodeURIComponent(hospital.userId)}`;
      }
      const res = await fetch(url);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      let filteredData = Array.isArray(data) ? data : [];
      
      if (hospital?.role === 'doctor') {
        filteredData = filteredData.filter(p => p.assigned_doctor === hospital.userId);
      } else if (adminDateFilter) {
        filteredData = filteredData.filter(p => p.timestamp === adminDateFilter);
      }
      setPatients(filteredData);
    } catch (e) {
      console.error('Records fetch error:', e);
      if (!silent) { setDbError('Could not load EHR from the API. Is the backend running on port 8000?'); setPatients([]); }
    } finally {
      if (!silent) setDbLoading(false);
    }
  }, [hospital?.id, hospital?.role, hospital?.userId, adminDateFilter]);

  useEffect(() => {
    if (currentView === 'database') loadRecords();
  }, [currentView, loadRecords]);

  // Poll FL status
  useEffect(() => {
    const interval = setInterval(async () => {
      try {
        const res = await fetch('http://127.0.0.1:8000/status');
        if (res.ok) {
          const data = await res.json();
          const prev = lastApiTrainingStatusRef.current;
          lastApiTrainingStatusRef.current = data.status;
          if (data.status === 'training') {
            suppressFlErrorRef.current = false;
            if (completeDismissTimerRef.current) { clearTimeout(completeDismissTimerRef.current); completeDismissTimerRef.current = null; }
            setFlStatus('training'); setFlErrorMessage(null); return;
          }
          if (data.status === 'complete') {
            suppressFlErrorRef.current = false; setFlErrorMessage(null);
            if (prev === 'training') {
              setFlStatus('complete');
              if (completeDismissTimerRef.current) clearTimeout(completeDismissTimerRef.current);
              completeDismissTimerRef.current = setTimeout(() => { setFlStatus('idle'); completeDismissTimerRef.current = null; }, 5000);
            }
            return;
          }
          if (data.status === 'error' && !suppressFlErrorRef.current) {
            setFlStatus('error');
            const msg = data.message || 'Federated training failed.';
            setFlErrorMessage(msg.length > 800 ? `${msg.slice(0, 800)}…` : msg);
            return;
          }
          if (data.status === 'idle') {
            suppressFlErrorRef.current = false; setFlErrorMessage(null);
            if (completeDismissTimerRef.current) { clearTimeout(completeDismissTimerRef.current); completeDismissTimerRef.current = null; }
            setFlStatus('idle');
          }
        }
      } catch (_) {}
    }, 2000);
    return () => { clearInterval(interval); if (completeDismissTimerRef.current) clearTimeout(completeDismissTimerRef.current); };
  }, []);

  const handlePredict = async (e) => {
    e.preventDefault();
    if (!hospital?.id) return;
    setPredictionStatus('predicting');
    try {
      const response = await fetch('http://127.0.0.1:8000/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          hospital_id: hospital.id,
          disease: selectedDisease,
          fields: formData,
        })
      });
      if (response.ok) {
        const data = await response.json();
        setPredictionResult(data.prediction);
        setPredictionStatus('result');
        setFlStatus('training');
        setReportData({
          ...formData,
          disease: selectedDisease,
          prediction: data.prediction,
          probability: data.probability,
          date: new Date().toLocaleDateString(),
          reportId: `REP-${Math.floor(100000 + Math.random() * 900000)}`
        });
        await loadRecords({ silent: true });
      }
    } catch (error) {
      console.error("API Error:", error);
      setPredictionStatus('idle');
    }
  };

  const handleViewHistoricalReport = (patientRow) => {
    const disease = (patientRow.disease || 'Heart').toLowerCase();
    const schema = DISEASE_SCHEMAS[disease] || DISEASE_SCHEMAS.heart;
    const fields = {};
    schema.fields.forEach(f => { fields[f.key] = patientRow[f.key] != null ? String(patientRow[f.key]) : ''; });
    setReportData({
      ...fields,
      disease,
      prediction: patientRow.result_label || (patientRow.result == 1 ? 'Positive (High Risk)' : 'Negative (Low Risk)'),
      probability: 0.85,
      date: patientRow.timestamp ? new Date(patientRow.timestamp).toLocaleDateString() : new Date().toLocaleDateString(),
      reportId: `REP-${String(patientRow.row).padStart(6, '0')}`
    });
    setShowReport(true);
  };

  // Filtered patients for DB tab
  const visiblePatients = dbDiseaseFilter === 'all'
    ? patients
    : patients.filter(p => (p.disease || '').toLowerCase() === dbDiseaseFilter);

  const schema = DISEASE_SCHEMAS[selectedDisease] || DISEASE_SCHEMAS.heart;
  const diseaseColor = schema.color;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', minHeight: '100vh', padding: '24px' }}>
      {/* Header */}
      <header className="glass-panel" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '16px 24px', marginBottom: '24px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <Activity color="var(--primary)" size={28} />
          <h2 style={{ margin: 0 }}>HealthFed AI <span style={{ color: 'var(--text-muted)', fontSize: '1rem', fontWeight: '400', marginLeft: '12px' }}>| {hospital.name} ({hospital.role === 'doctor' ? 'Doctor' : 'Admin'})</span></h2>
        </div>
        <button className="btn-secondary" onClick={onLogout} style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <LogOut size={16} /> Secure Logout
        </button>
      </header>

      <div style={{ display: 'flex', gap: '24px', flex: 1 }}>
        {/* Left Navigation */}
        <div className="glass-panel" style={{ width: '280px', padding: '24px', display: 'flex', flexDirection: 'column', gap: '12px' }}>
          <h3 style={{ margin: '0 0 12px 0', color: 'var(--primary)' }}>Navigation</h3>

          <button
            className={`btn-secondary ${currentView === 'database' ? 'active' : ''}`}
            onClick={() => setCurrentView('database')}
            style={{ display: 'flex', alignItems: 'center', gap: '12px', width: '100%', justifyContent: 'flex-start',
              background: currentView === 'database' ? 'rgba(14,165,233,0.1)' : 'transparent',
              border: currentView === 'database' ? '1px solid var(--primary)' : '1px solid var(--surface-border)' }}
          >
            <Database size={20} />
            {hospital?.role === 'doctor' ? 'View Patient Reports' : 'View Database'}
          </button>

          {hospital?.role !== 'doctor' && (
            <button
              className={`btn-secondary ${currentView === 'predict' ? 'active' : ''}`}
              onClick={() => setCurrentView('predict')}
              style={{ display: 'flex', alignItems: 'center', gap: '12px', width: '100%', justifyContent: 'flex-start',
                background: currentView === 'predict' ? 'rgba(14,165,233,0.1)' : 'transparent',
                border: currentView === 'predict' ? '1px solid var(--primary)' : '1px solid var(--surface-border)' }}
            >
              <UserPlus size={20} /> Predict New Patient
            </button>
          )}

          {/* Disease Legend */}
          <div style={{ marginTop: '16px', padding: '12px', background: 'rgba(255,255,255,0.03)', borderRadius: '8px', border: '1px solid var(--surface-border)' }}>
            <p style={{ margin: '0 0 8px 0', fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Disease Types</p>
            {DISEASE_LIST.map(d => (
              <div key={d} style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>
                <div style={{ width: '10px', height: '10px', borderRadius: '50%', background: DISEASE_SCHEMAS[d].color, flexShrink: 0 }} />
                <span style={{ fontSize: '0.8125rem', color: 'var(--text-muted)' }}>{DISEASE_SCHEMAS[d].label}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Right Content */}
        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: '24px' }}>

          {/* ── Database View ── */}
          {currentView === 'database' && (
            <div className="glass-panel" style={{ padding: '24px', display: 'flex', flexDirection: 'column', flex: 1, minHeight: 0 }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '16px', marginBottom: '16px', flexWrap: 'wrap' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                  <Database color="var(--primary)" />
                  <div>
                    <h3 style={{ margin: 0 }}>{hospital?.role === 'doctor' ? 'Clinical Reports' : 'Local Patient Database'}</h3>
                    <p style={{ margin: '4px 0 0 0', fontSize: '0.8125rem', color: 'var(--text-muted)' }}>
                      All diseases with their disease-specific features
                    </p>
                  </div>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px', flexWrap: 'wrap' }}>
                  {/* Disease filter - hidden for specialists */}
                  {hospital?.role !== 'doctor' && (
                    <select className="input-field" style={{ padding: '6px 12px', minHeight: '36px', width: 'auto' }}
                      value={dbDiseaseFilter} onChange={e => setDbDiseaseFilter(e.target.value)}>
                      <option value="all">All Diseases</option>
                      {DISEASE_LIST.map(d => <option key={d} value={d}>{DISEASE_SCHEMAS[d].label}</option>)}
                    </select>
                  )}
                  {hospital?.role !== 'doctor' && (
                    <input type="date" className="input-field" style={{ padding: '6px 12px', minHeight: '36px', width: 'auto' }}
                      value={adminDateFilter} onChange={e => setAdminDateFilter(e.target.value)} title="Filter by date" />
                  )}
                  <button type="button" className="btn-secondary" onClick={() => loadRecords()} disabled={dbLoading}
                    style={{ display: 'inline-flex', alignItems: 'center', gap: '8px', minHeight: '36px' }}>
                    <RefreshCw size={16} className={dbLoading ? 'spin-icon' : ''} /> Refresh
                  </button>
                </div>
              </div>

              {dbError && (
                <div style={{ marginBottom: '16px', padding: '12px 16px', borderRadius: '8px', background: 'rgba(239,68,68,0.12)', border: '1px solid rgba(239,68,68,0.35)', fontSize: '0.875rem' }}>
                  {dbError}
                </div>
              )}

              {dbLoading && visiblePatients.length === 0 && !dbError ? (
                <div className="database-empty">Loading records…</div>
              ) : visiblePatients.length === 0 ? (
                <div className="database-empty">
                  {hospital?.role === 'doctor'
                    ? <>No reports have been assigned to you today.</>
                    : <>No saved patients yet for <strong style={{ color: 'var(--text-main)' }}>{hospital?.id}</strong>. Use <em>Predict New Patient</em> to add the first record.</>}
                </div>
              ) : (
                <DiseaseGroupedTable patients={visiblePatients} hospital={hospital} onReport={handleViewHistoricalReport} />
              )}
            </div>
          )}

          {/* ── Predict View ── */}
          {currentView === 'predict' && (
            <>
              <div className="glass-panel" style={{ padding: '24px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '20px' }}>
                  <UserPlus color="var(--primary)" />
                  <h3 style={{ margin: 0 }}>New Patient Prediction</h3>
                </div>

                <form onSubmit={handlePredict} style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px' }}>
                  {/* Disease selector */}
                  <div style={{ gridColumn: '1 / -1', marginBottom: '8px' }}>
                    <label style={{ display: 'block', fontSize: '0.875rem', marginBottom: '6px', color: 'white', fontWeight: '600' }}>
                      Select Disease / Specialist Context
                    </label>
                    <select className="input-field" value={selectedDisease}
                      onChange={e => handleDiseaseChange(e.target.value)}
                      style={{ padding: '10px 16px', fontWeight: '600' }}>
                      {DISEASE_LIST.map(d => (
                        <option key={d} value={d}>
                          {DISEASE_SCHEMAS[d].label}
                        </option>
                      ))}
                    </select>
                  </div>

                  {/* Dynamic disease-specific fields */}
                  {schema.fields.map(field => (
                    <div key={field.key}>
                      <label style={{ display: 'block', fontSize: '0.875rem', marginBottom: '6px', color: 'var(--text-muted)' }}>
                        {field.label}
                      </label>
                      {field.type === 'select' ? (
                        <select className="input-field" value={formData[field.key] ?? ''} required
                          onChange={e => setFormData({ ...formData, [field.key]: e.target.value })}>
                          <option value="">Select</option>
                          {field.options.map(o => <option key={o.v} value={o.v}>{o.l}</option>)}
                        </select>
                      ) : (
                        <input type="number" className="input-field" value={formData[field.key] ?? ''}
                          step={field.step || '1'} placeholder={field.placeholder || ''} required
                          onChange={e => setFormData({ ...formData, [field.key]: e.target.value })} />
                      )}
                    </div>
                  ))}

                  <div style={{ gridColumn: '1 / -1', display: 'flex', justifyContent: 'center', marginTop: '16px' }}>
                    <button type="submit" className="btn-primary" disabled={predictionStatus === 'predicting'}
                      style={{ background: diseaseColor, borderColor: diseaseColor }}>
                      {predictionStatus === 'predicting' ? 'Analyzing via FL Model...' : `Run ${schema.label} Prediction`}
                    </button>
                  </div>
                </form>

                {predictionStatus === 'result' && (
                  <div style={{ marginTop: '20px', padding: '16px', borderRadius: '8px', background: 'rgba(255,255,255,0.05)', border: `1px solid ${diseaseColor}44` }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '8px' }}>
                      <FileHeart size={20} color={isHighRiskLabel(predictionResult) ? 'var(--danger)' : 'var(--success)'} />
                      <h4 style={{ margin: 0 }}>Prediction Result — <span style={{ color: diseaseColor }}>{schema.label}</span></h4>
                    </div>
                    <p>Risk Assessment: <strong style={{ color: isHighRiskLabel(predictionResult) ? 'var(--danger)' : 'var(--success)' }}>{predictionResult}</strong></p>
                    <p style={{ fontSize: '0.875rem', color: 'var(--text-muted)', marginTop: '4px' }}>Patient added to EHR. FL training triggered.</p>
                    <button className="btn-primary" onClick={() => setShowReport(true)}
                      style={{ marginTop: '16px', display: 'flex', alignItems: 'center', gap: '8px', background: 'var(--success)', borderColor: 'var(--success)' }}>
                      <FileText size={18} /> View Medical Report
                    </button>
                  </div>
                )}
              </div>

              {/* FL Status */}
              <div className="glass-panel" style={{ padding: '24px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '20px' }}>
                  <Server color="var(--primary)" /> <h3>Federated Learning Status</h3>
                </div>
                {flStatus === 'error' && flErrorMessage && (
                  <div style={{ marginBottom: '20px', padding: '14px 16px', background: 'rgba(239,68,68,0.12)', border: '1px solid rgba(239,68,68,0.35)', borderRadius: '8px', fontSize: '0.8125rem', lineHeight: 1.5, color: '#fecaca' }}>
                    <strong style={{ display: 'block', marginBottom: '6px' }}>Training could not finish</strong>
                    <span style={{ whiteSpace: 'pre-wrap', wordBreak: 'break-word' }}>{flErrorMessage}</span>
                    <button type="button" className="btn-secondary" style={{ marginTop: '12px' }}
                      onClick={() => { suppressFlErrorRef.current = true; setFlStatus('idle'); setFlErrorMessage(null); }}>
                      Dismiss
                    </button>
                  </div>
                )}
                <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                  <StatusRow active={flStatus === 'training' || flStatus === 'complete'} icon={<Database size={18} />} text="Saving securely to Local EHR" />
                  <StatusRow active={flStatus === 'training' || flStatus === 'complete'} icon={<CheckSquare2 size={18} />} text="Training Local PyTorch Model" loading={flStatus === 'training'} />
                  <StatusRow active={flStatus === 'training' || flStatus === 'complete'} icon={<ShieldCheck size={18} />}
                    text={flStatus === 'complete' ? 'TLS Encrypted Global Sync (Flower) — Done' : flStatus === 'training' ? 'TLS Encrypted Global Sync (Flower) — In Progress' : 'TLS Encrypted Global Sync (Flower) — Pending'}
                    loading={flStatus === 'training'} />
                </div>
                {flStatus === 'complete' && (
                  <div style={{ marginTop: '24px', padding: '12px', background: 'rgba(16,185,129,0.1)', border: '1px solid var(--success)', borderRadius: '8px', color: 'var(--success)', textAlign: 'center', fontSize: '0.875rem' }}>
                    Global Model Updated Successfully
                  </div>
                )}
                {flStatus === 'idle' && (
                  <div style={{ marginTop: '24px', textAlign: 'center', color: 'var(--text-muted)', fontSize: '0.875rem' }}>
                    Waiting for new data to trigger training...
                  </div>
                )}
              </div>
            </>
          )}

          {/* Report Modal */}
          {showReport && reportData && (
            <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.85)', display: 'flex', justifyContent: 'center', alignItems: 'center', zIndex: 1000, padding: '20px' }}>
              <div className="glass-panel" style={{ width: '100%', maxWidth: '900px', maxHeight: '90vh', overflowY: 'auto', position: 'relative', padding: 0, background: 'white', color: '#334155' }}>
                <button onClick={() => setShowReport(false)}
                  style={{ position: 'absolute', top: '16px', right: '16px', background: '#f1f5f9', border: 'none', borderRadius: '50%', width: '32px', height: '32px', display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer', color: '#64748b', zIndex: 10 }}>
                  <X size={20} />
                </button>
                <Report data={reportData} hospital={hospital} onClose={() => setShowReport(false)} />
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

// ── Disease-grouped table ──────────────────────────────────────────────────
function DiseaseGroupedTable({ patients, hospital, onReport }) {
  // Group by disease
  const groups = {};
  patients.forEach(p => {
    const d = (p.disease || 'Heart').toLowerCase();
    if (!groups[d]) groups[d] = [];
    groups[d].push(p);
  });

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px', overflowY: 'auto', flex: 1 }}>
      {Object.entries(groups).map(([disease, rows]) => {
        const schema = DISEASE_SCHEMAS[disease] || DISEASE_SCHEMAS.heart;
        return (
          <div key={disease}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '10px' }}>
              <div style={{ width: '12px', height: '12px', borderRadius: '50%', background: schema.color }} />
              <h4 style={{ margin: 0, color: schema.color, fontSize: '0.9375rem' }}>{schema.label}</h4>
              <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>({rows.length} records)</span>
            </div>
            <div className="database-scroll">
              <table className="data-table data-table--compact">
                <thead>
                  <tr>
                    <th>Patient ID</th>
                    {hospital?.role !== 'doctor' && schema.tableHeaders.map(h => <th key={h}>{h}</th>)}
                    <th>Result</th>
                    <th>Date</th>
                    <th>Action</th>
                  </tr>
                </thead>
                <tbody>
                  {rows.map(p => {
                    const label = p.result_label ?? formatResultLabel(p.result);
                    const high = isHighRiskLabel(label);
                    return (
                      <tr key={`${p.row}-${disease}`}>
                        <td><strong style={{ color: 'var(--text-main)' }}>PAT-{String(p.row).padStart(4, '0')}</strong></td>
                        {hospital?.role !== 'doctor' && schema.tableKeys.map(k => (
                          <td key={k}>{disease === 'heart' && k === 'sex' ? formatSex(p[k]) : formatCell(p[k])}</td>
                        ))}
                        <td><span className={`status-badge ${high ? 'status-negative' : 'status-positive'}`}>{label}</span></td>
                        <td style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{p.timestamp || '—'}</td>
                        <td>
                          <button className="btn-secondary"
                            style={{ padding: '4px 8px', fontSize: '0.75rem', display: 'flex', alignItems: 'center', gap: '4px' }}
                            onClick={() => onReport(p)}>
                            <FileText size={14} /> Report
                          </button>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        );
      })}
    </div>
  );
}

// ── Helpers ────────────────────────────────────────────────────────────────
function formatSex(value) {
  const n = parseInt(String(value), 10);
  if (n === 0) return 'Female';
  if (n === 1) return 'Male';
  return value === '' || value == null ? '—' : String(value);
}

function formatCell(value) {
  if (value === '' || value == null || (typeof value === 'number' && isNaN(value))) return '—';
  if (typeof value === 'number' && !Number.isInteger(value)) return String(Math.round(value * 100) / 100);
  return String(value);
}

function formatResultLabel(result) {
  if (result === 1 || result === '1' || result === true) return 'Positive (High Risk)';
  if (result === 0 || result === '0' || result === false) return 'Negative (Low Risk)';
  const s = String(result);
  if (s.toLowerCase().includes('positive')) return 'Positive (High Risk)';
  if (s.toLowerCase().includes('negative')) return 'Negative (Low Risk)';
  return s || '—';
}

function isHighRiskLabel(label) {
  return typeof label === 'string' && label.includes('High Risk');
}

function StatusRow({ active, icon, text, loading }) {
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: '12px', padding: '12px', borderRadius: '8px',
      background: active ? 'rgba(14,165,233,0.1)' : 'rgba(255,255,255,0.02)',
      border: `1px solid ${active ? 'var(--primary-glow)' : 'transparent'}`,
      color: active ? 'white' : 'var(--text-muted)', transition: 'all 0.3s' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', width: '24px', height: '24px', color: active ? 'var(--primary)' : 'inherit' }}>{icon}</div>
      <span style={{ flex: 1, fontSize: '0.875rem', fontWeight: active ? '500' : '400' }}>{text}</span>
      {loading && (
        <div style={{ width: '16px', height: '16px', borderRadius: '50%', border: '2px solid var(--primary)', borderTopColor: 'transparent', animation: 'fl-spin 0.8s linear infinite', flexShrink: 0 }} />
      )}
      <style>{`@keyframes fl-spin { to { transform: rotate(360deg); } }`}</style>
    </div>
  );
}
