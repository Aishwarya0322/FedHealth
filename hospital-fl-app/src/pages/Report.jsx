import React, { useRef, useState } from 'react';
import { Download, Activity, Heart, Droplets, Wind, FlaskConical, User, Calendar, Clipboard, Shield, Printer, RefreshCw, FileText, ArrowLeft, X } from 'lucide-react';
import { jsPDF } from 'jspdf';
import html2canvas from 'html2canvas';

// ─── Disease display configs ───────────────────────────────────────────────
const DISEASE_DISPLAY = {
  heart: {
    label: 'Cardiology',
    dept: 'Department of Cardiology & Advanced Diagnostics',
    color: '#ef4444',
    Icon: Heart,
    referral: 'Cardiological Assessment',
    sections: (data) => [
      { label: 'Resting Blood Pressure', value: `${data.trestbps || '—'} mm Hg` },
      { label: 'Serum Cholesterol',       value: `${data.chol || '—'} mg/dl` },
      { label: 'Chest Pain Type',         value: `Type ${data.cp ?? '—'}` },
      { label: 'Fasting Blood Sugar',     value: data.fbs === '1' ? '> 120 mg/dl' : '≤ 120 mg/dl' },
      { label: 'Max Heart Rate',          value: `${data.thalach || '—'} bpm` },
      { label: 'Resting ECG',             value: `Type ${data.restecg ?? '—'}` },
      { label: 'ST Depression',           value: data.oldpeak || '—' },
      { label: 'Major Vessels',           value: data.ca ?? '—' },
      { label: 'Exercise Angina',         value: data.exang === '1' ? 'Yes' : 'No' },
      { label: 'ST Slope',               value: ['Upsloping','Flat','Downsloping'][parseInt(data.slope)] || data.slope || '—' },
      { label: 'Thalassemia',            value: data.thal === '3' ? 'Normal' : data.thal === '6' ? 'Fixed Defect' : data.thal === '7' ? 'Reversible Defect' : data.thal || '—' },
    ],
    highRiskRecs: [
      'Urgent consultation with a cardiologist is highly recommended.',
      'Monitor blood pressure and fasting sugars daily.',
      'Avoid strenuous physical activity until cleared by a physician.',
      'Review of medications (statins/anti-hypertensives) may be required.',
    ],
    lowRiskRecs: [
      'Maintain a heart-healthy diet low in saturated fats and sodium.',
      'Continue regular aerobic exercise (150 mins/week).',
      'Schedule a routine follow-up check in 6 months.',
      'Excellent metrics observed in fasting sugars and ECG profile.',
    ],
  },


  cancer: {
    label: 'Oncology',
    dept: 'Department of Oncology & Pulmonary Medicine',
    color: '#f59e0b',
    Icon: Wind,
    referral: 'Lung Cancer Risk Profile Assessment',
    sections: (data) => [
      { label: 'Air Pollution Exposure',   value: `${data['Air Pollution'] || '—'} / 9` },
      { label: 'Alcohol Use',             value: `${data['Alcohol use'] || '—'} / 9` },
      { label: 'Dust Allergy',            value: `${data['Dust Allergy'] || '—'} / 9` },
      { label: 'Occupational Hazards',    value: `${data['OccuPational Hazards'] || '—'} / 9` },
      { label: 'Genetic Risk',            value: `${data['Genetic Risk'] || '—'} / 9` },
      { label: 'Chronic Lung Disease',    value: data['Chronic Lung Disease'] === '1' || data['Chronic Lung Disease'] === 1 ? 'Yes' : 'No' },
      { label: 'Balanced Diet',           value: `${data['Balanced Diet'] || '—'} / 9` },
      { label: 'Obesity',                value: `${data.Obesity || '—'} / 9` },
      { label: 'Smoking',                value: `${data.Smoking || '—'} / 9` },
      { label: 'Passive Smoker',          value: `${data['Passive Smoker'] || '—'} / 9` },
      { label: 'Chest Pain',             value: `${data['Chest Pain'] || '—'} / 9` },
      { label: 'Coughing of Blood',      value: `${data['Coughing of Blood'] || '—'} / 9` },
      { label: 'Fatigue',                value: `${data['Fatigue'] || '—'} / 9` },
      { label: 'Weight Loss',            value: `${data['Weight Loss'] || '—'} / 9` },
      { label: 'Shortness of Breath',    value: `${data['Shortness of Breath'] || '—'} / 9` },
      { label: 'Wheezing',               value: `${data['Wheezing'] || '—'} / 9` },
      { label: 'Swallowing Difficulty',  value: `${data['Swallowing Difficulty'] || '—'} / 9` },
      { label: 'Clubbing of Nails',      value: `${data['Clubbing of Finger Nails'] || '—'} / 9` },
      { label: 'Frequent Cold',          value: `${data['Frequent Cold'] || '—'} / 9` },
      { label: 'Dry Cough',              value: `${data['Dry Cough'] || '—'} / 9` },
      { label: 'Snoring',                value: `${data['Snoring'] || '—'} / 9` },
    ],
    highRiskRecs: [
      'Immediate consultation with an oncologist is strongly recommended.',
      'Schedule CT chest scan and sputum cytology.',
      'Cessation of smoking and alcohol is mandatory.',
      'Refer for pulmonary function tests and bronchoscopy evaluation.',
    ],
    lowRiskRecs: [
      'Avoid smoking, passive smoke, and high-pollution environments.',
      'Maintain a balanced diet rich in antioxidants.',
      'Annual chest X-ray for individuals with occupational exposure.',
      'Exercise regularly to support respiratory health.',
    ],
  },

  anaemia: {
    label: 'Haematology',
    dept: 'Department of Haematology & Blood Disorders',
    color: '#8b5cf6',
    Icon: FlaskConical,
    referral: 'Anaemia Detection via Blood Smear Analysis',
    sections: (data) => [
      { label: '% Red Pixel',    value: `${data['%Red Pixel'] ?? data.Red_Pixel ?? '—'} %` },
      { label: '% Green Pixel',  value: `${data['%Green Pixel'] ?? data.Green_Pixel ?? '—'} %` },
      { label: '% Blue Pixel',   value: `${data['%Blue Pixel'] ?? data.Blue_Pixel ?? '—'} %` },
      { label: 'Haemoglobin',    value: `${data.Hb || '—'} g/dl` },
    ],
    highRiskRecs: [
      'Consult a haematologist for comprehensive blood panel.',
      'Iron supplementation or B12/folate therapy may be required.',
      'Investigate underlying causes: bleeding, nutritional deficiency, hemolysis.',
      'Repeat CBC in 4–6 weeks after initiating treatment.',
    ],
    lowRiskRecs: [
      'Maintain iron-rich dietary habits (lean meat, legumes, leafy greens).',
      'Annual haemoglobin check recommended.',
      'Stay well-hydrated and avoid excessive physical exertion.',
      'No immediate intervention required based on current assessment.',
    ],
  },
};

// ─── Helpers ───────────────────────────────────────────────────────────────
function fmt(v) {
  if (v === '' || v == null) return '—';
  if (typeof v === 'number') return String(Math.round(v * 100) / 100);
  return String(v);
}

function getSexLabel(sex) {
  if (sex === '0' || sex === 0) return 'Female';
  if (sex === '1' || sex === 1) return 'Male';
  return fmt(sex);
}

// ─── Main Report Component ─────────────────────────────────────────────────
const Report = ({ data, hospital, onClose }) => {
  const reportRef = useRef();
  const [isGenerating, setIsGenerating] = useState(false);

  const disease = (data?.disease || 'heart').toLowerCase();
  const display = DISEASE_DISPLAY[disease] || DISEASE_DISPLAY.heart;
  const { Icon, color } = display;
  const riskColor = (data?.prediction || '').includes('High Risk') ? color : '#10b981';

  const handleDownloadPDF = async () => {
    if (isGenerating) return;
    setIsGenerating(true);
    try {
      const element = reportRef.current;
      if (!element) throw new Error('Report element not found');
      await new Promise(r => setTimeout(r, 150));
      const canvas = await html2canvas(element, {
        scale: 3,
        useCORS: true,
        logging: false,
        backgroundColor: '#ffffff',
        onclone: (doc) => {
          const el = doc.getElementById('printable-report');
          if (el) { el.style.boxShadow = 'none'; el.style.border = 'none'; }
        }
      });
      const imgData = canvas.toDataURL('image/png');
      const pdf = new jsPDF({ orientation: 'portrait', unit: 'mm', format: 'a4', compress: true });
      const pdfWidth = pdf.internal.pageSize.getWidth();
      const pdfHeight = (canvas.height * pdfWidth) / canvas.width;
      pdf.addImage(imgData, 'PNG', 0, 0, pdfWidth, pdfHeight, undefined, 'FAST');
      pdf.save(`${(hospital?.name || 'Hospital').replace(/\s+/g, '_')}_${display.label}_Report_${data.reportId}.pdf`);
    } catch (err) {
      console.error('PDF generation failed:', err);
      alert("Use 'Print / Save' if automatic download fails.");
    } finally {
      setIsGenerating(false);
    }
  };

  const sections = display.sections(data);
  const recs = (data?.prediction || '').includes('High Risk') ? display.highRiskRecs : display.lowRiskRecs;

  // Build pairs for 2-column layout
  const pairs = [];
  for (let i = 0; i < sections.length; i += 2) {
    pairs.push([sections[i], sections[i + 1]]);
  }

  return (
    <div style={{ background: '#f1f5f9', color: '#1e293b', minHeight: '100%' }}>
      <style>{`
        @media print {
          body * { display: none !important; }
          #printable-report, #printable-report * { display: block !important; visibility: visible !important; }
          #printable-report { position: absolute; left: 0; top: 0; width: 100% !important; padding: 0 !important; margin: 0 !important; box-shadow: none !important; display: block !important; }
          .no-print { display: none !important; }
        }
        @keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
        .spin-icon { animation: spin 1s linear infinite; }
      `}</style>

      {/* ── Action bar ── */}
      <div className="no-print" style={{ padding: '16px 24px', background: '#ffffff', borderBottom: '1px solid #e2e8f0', display: 'flex', justifyContent: 'space-between', alignItems: 'center', position: 'sticky', top: 0, zIndex: 100 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <button onClick={onClose} className="btn-secondary" style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '8px 14px', borderRadius: '8px', border: '1px solid #e2e8f0', background: '#f8fafc', cursor: 'pointer', color: '#64748b' }}>
            <ArrowLeft size={18} /> Back
          </button>
          <div style={{ background: `${color}22`, padding: '8px', borderRadius: '8px' }}>
            <Icon size={20} color={color} />
          </div>
          <h3 style={{ margin: 0, fontSize: '1.1rem', fontWeight: 600, color: '#0f172a' }}>
            {display.label} Report Preview
          </h3>
        </div>
        {hospital?.role !== 'doctor' && (
          <div style={{ display: 'flex', gap: '8px' }}>
            <button onClick={() => window.print()} className="btn-secondary" style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '8px 14px', fontSize: '0.875rem' }}>
              <Printer size={16} /> Print / Save PDF
            </button>
            <button onClick={handleDownloadPDF} className="btn-primary" disabled={isGenerating}
              style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '8px 16px', fontSize: '0.875rem', background: isGenerating ? '#94a3b8' : color, borderColor: color, opacity: isGenerating ? 0.7 : 1 }}>
              {isGenerating ? <><RefreshCw size={16} className="spin-icon" /> Generating…</> : <><Download size={16} /> Download</>}
            </button>
          </div>
        )}
      </div>

      {/* ── Printable Report ── */}
      <div ref={reportRef} id="printable-report" data-report-container="true"
        style={{ width: '210mm', minHeight: '297mm', margin: '0 auto', padding: '20mm', background: '#ffffff', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)', fontFamily: "'Inter', system-ui, sans-serif" }}>

        {/* Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', borderBottom: `2px solid ${color}`, paddingBottom: '20px', marginBottom: '28px' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '6px' }}>
              <Activity size={30} color={color} />
              <h1 style={{ margin: 0, fontSize: '22px', fontWeight: 800, color: '#0f172a' }}>{hospital?.name || 'Central General Hospital'}</h1>
            </div>
            <p style={{ margin: 0, fontSize: '13px', color: '#64748b' }}>{display.dept}</p>
            <p style={{ margin: '3px 0 0 0', fontSize: '11px', color: '#94a3b8' }}>Federated Learning Network — Member ID: {hospital?.id || 'HOSP-001'}</p>
          </div>
          <div style={{ textAlign: 'right' }}>
            <span style={{ display: 'inline-block', background: `${color}18`, color, fontWeight: 700, fontSize: '11px', padding: '4px 10px', borderRadius: '20px', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: '8px' }}>
              {display.label} Report
            </span>
            <p style={{ margin: 0, fontSize: '13px', color: '#64748b' }}><strong>Report ID:</strong> {data.reportId}</p>
            <p style={{ margin: '3px 0 0 0', fontSize: '13px', color: '#64748b' }}><strong>Date:</strong> {data.date}</p>
          </div>
        </div>

        {/* Patient Info */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginBottom: '28px', padding: '14px', background: '#f8fafc', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
          <div>
            <h4 style={{ margin: '0 0 8px 0', fontSize: '11px', color, textTransform: 'uppercase', letterSpacing: '0.06em' }}>Patient Information</h4>
            <p style={{ margin: 0, fontSize: '13px' }}><User size={13} style={{ marginRight: '6px', verticalAlign: 'middle', color: '#64748b' }} /><strong>Name:</strong> Confidential Patient</p>
            <p style={{ margin: '4px 0 0 0', fontSize: '13px' }}>
              <Calendar size={13} style={{ marginRight: '6px', verticalAlign: 'middle', color: '#64748b' }} />
              <strong>Age / Sex:</strong>{' '}
              {data.age ? `${data.age} yrs` : '—'} / {getSexLabel(data.sex ?? data.Sex ?? data.Gender)}
            </p>
          </div>
          <div>
            <h4 style={{ margin: '0 0 8px 0', fontSize: '11px', color, textTransform: 'uppercase', letterSpacing: '0.06em' }}>Clinical Context</h4>
            <p style={{ margin: 0, fontSize: '13px' }}><Clipboard size={13} style={{ marginRight: '6px', verticalAlign: 'middle', color: '#64748b' }} /><strong>Referral Reason:</strong> {display.referral}</p>
            <p style={{ margin: '4px 0 0 0', fontSize: '13px' }}><Shield size={13} style={{ marginRight: '6px', verticalAlign: 'middle', color: '#64748b' }} /><strong>Data Security:</strong> Differential Privacy Enabled</p>
          </div>
        </div>

        {/* Clinical Data Table */}
        <div style={{ marginBottom: '28px' }}>
          <h3 style={{ fontSize: '15px', borderBottom: '1px solid #e2e8f0', paddingBottom: '8px', marginBottom: '12px', fontWeight: 700 }}>
            1. Clinical Observations &amp; Diagnostic Tests
          </h3>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '12.5px' }}>
            <tbody>
              {pairs.map((pair, i) => (
                <tr key={i} style={{ background: i % 2 === 0 ? '#f8fafc' : '#ffffff' }}>
                  <td style={{ padding: '7px 10px', border: '1px solid #e2e8f0', width: '22%', fontWeight: 600, color: '#475569' }}>{pair[0]?.label}</td>
                  <td style={{ padding: '7px 10px', border: '1px solid #e2e8f0', width: '28%' }}>{fmt(pair[0]?.value)}</td>
                  {pair[1] ? (
                    <>
                      <td style={{ padding: '7px 10px', border: '1px solid #e2e8f0', width: '22%', fontWeight: 600, color: '#475569' }}>{pair[1].label}</td>
                      <td style={{ padding: '7px 10px', border: '1px solid #e2e8f0', width: '28%' }}>{fmt(pair[1].value)}</td>
                    </>
                  ) : <><td style={{ border: '1px solid #e2e8f0' }} /><td style={{ border: '1px solid #e2e8f0' }} /></>}
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* AI Result */}
        <div style={{ marginBottom: '28px' }}>
          <h3 style={{ fontSize: '15px', borderBottom: '1px solid #e2e8f0', paddingBottom: '8px', marginBottom: '14px', fontWeight: 700 }}>
            2. AI-Assisted Diagnostic Evaluation
          </h3>
          <div style={{ padding: '18px 20px', border: `2px solid ${riskColor}`, borderRadius: '12px', display: 'flex', gap: '18px', alignItems: 'center' }}>
            <div style={{ background: riskColor, borderRadius: '50%', minWidth: '48px', height: '48px', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'white' }}>
              <Icon size={28} />
            </div>
            <div>
              <p style={{ margin: 0, fontSize: '13px', color: '#64748b' }}>Diagnostic Impression ({display.label}):</p>
              <h2 style={{ margin: '4px 0', color: riskColor, fontSize: '22px', fontWeight: 800 }}>{data.prediction}</h2>
              <p style={{ margin: 0, fontSize: '13px' }}><strong>Confidence Score:</strong> {((data.probability || 0) * 100).toFixed(2)}%</p>
            </div>
          </div>
          <p style={{ fontSize: '11px', color: '#94a3b8', marginTop: '8px', fontStyle: 'italic' }}>
            * This evaluation is generated by the federated global model aggregate. All local data remained on-site during training (Flower FL framework).
          </p>
        </div>

        {/* Recommendations */}
        <div style={{ marginBottom: '40px' }}>
          <h3 style={{ fontSize: '15px', borderBottom: '1px solid #e2e8f0', paddingBottom: '8px', marginBottom: '12px', fontWeight: 700 }}>
            3. Clinical Recommendations
          </h3>
          <div style={{ padding: '14px 16px', background: '#f1f5f9', borderRadius: '8px', fontSize: '13px', lineHeight: '1.7' }}>
            <ul style={{ margin: 0, paddingLeft: '18px' }}>
              {recs.map((r, i) => <li key={i}>{r}</li>)}
            </ul>
          </div>
        </div>

        {/* Footer */}
        <div style={{ paddingTop: '32px', borderTop: '1px solid #e2e8f0', display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end' }}>
          <div>
            <div style={{ width: '180px', borderBottom: '1px solid #334155', marginBottom: '8px' }} />
            <p style={{ margin: 0, fontSize: '11.5px', fontWeight: 600 }}>Clinical Reviewer / AI System</p>
            <p style={{ margin: 0, fontSize: '10px', color: '#64748b' }}>Issued by HealthFed AI Network — {display.label} Module</p>
          </div>
          <div style={{ textAlign: 'right', maxWidth: '280px' }}>
            <p style={{ margin: 0, fontSize: '9px', color: '#94a3b8', fontStyle: 'italic' }}>
              Disclaimer: This report is provided by an AI-assisted Federated Learning system for diagnostic support.
              Final clinical decisions must be made by a licensed medical professional in accordance with facility protocols.
            </p>
          </div>
        </div>

      </div>
    </div>
  );
};

export default Report;
