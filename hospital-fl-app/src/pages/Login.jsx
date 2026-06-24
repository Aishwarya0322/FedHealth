import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Activity, Shield, AlertCircle, Eye, EyeOff } from 'lucide-react';
import { validateCredentials, saveAuthToStorage } from '../auth';

export default function Login({ onLogin }) {
  const [role, setRole] = useState('admin');
  const [hospitalId, setHospitalId] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    // Validate credentials
    const result = validateCredentials(hospitalId, password);

    if (!result.valid) {
      setError(result.message);
      setLoading(false);
      return;
    }

    if (result.hospital.role !== role) {
      setError(`Access denied. Please ensure you are logging in with ${role === 'admin' ? 'an admin' : 'a doctor'} account.`);
      setLoading(false);
      return;
    }

    // Simulate network delay for authentication
    setTimeout(() => {
      const authData = result.hospital;
      
      // Save to localStorage for persistence
      saveAuthToStorage(authData);
      
      // Update parent state
      onLogin(authData);
      
      // Navigate to dashboard (replace history so back button does not return to login)
      navigate('/dashboard', { replace: true });
      setLoading(false);
    }, 500);
  };

  return (
    <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '20px' }}>
      <div className="glass-panel" style={{ width: '100%', maxWidth: '440px', padding: '40px' }}>
        <div style={{ textAlign: 'center', marginBottom: '32px' }}>
          <div style={{ display: 'inline-flex', padding: '16px', background: 'rgba(14, 165, 233, 0.1)', borderRadius: '20px', marginBottom: '16px' }}>
            <Activity size={32} color="var(--primary)" />
          </div>
          <h1 style={{ fontSize: '1.75rem', fontWeight: '600', marginBottom: '8px' }}>HealthFed AI</h1>
          <p style={{ color: 'var(--text-muted)' }}>Collaborative AI for Healthcare</p>
        </div>

        {error && (
          <div style={{ 
            padding: '12px 16px', 
            background: 'rgba(239, 68, 68, 0.1)', 
            border: '1px solid rgba(239, 68, 68, 0.3)',
            borderRadius: '8px',
            marginBottom: '20px',
            display: 'flex',
            alignItems: 'center',
            gap: '12px',
            color: '#ef4444'
          }}>
            <AlertCircle size={18} />
            <span style={{ fontSize: '0.875rem' }}>{error}</span>
          </div>
        )}

        <div style={{ display: 'flex', background: 'rgba(0,0,0,0.2)', padding: '6px', borderRadius: '12px', marginBottom: '24px' }}>
          <button 
            type="button"
            onClick={() => { setRole('admin'); setHospitalId(''); setPassword(''); setError(''); }}
            style={{ flex: 1, padding: '10px', borderRadius: '8px', border: 'none', background: role === 'admin' ? 'var(--primary)' : 'transparent', color: role === 'admin' ? 'white' : 'var(--text-muted)', cursor: 'pointer', fontWeight: '500', transition: 'all 0.2s' }}
          >
            Hospital Admin
          </button>
          <button 
            type="button"
            onClick={() => { setRole('doctor'); setHospitalId(''); setPassword(''); setError(''); }}
            style={{ flex: 1, padding: '10px', borderRadius: '8px', border: 'none', background: role === 'doctor' ? 'var(--primary)' : 'transparent', color: role === 'doctor' ? 'white' : 'var(--text-muted)', cursor: 'pointer', fontWeight: '500', transition: 'all 0.2s' }}
          >
            Doctor
          </button>
        </div>

        <form onSubmit={handleLogin} style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          <div>
            <label style={{ display: 'block', marginBottom: '8px', fontSize: '0.875rem', color: 'var(--text-muted)' }}>
              {role === 'admin' ? 'Admin ID' : 'Doctor ID'}
            </label>
            <input 
              type="text" 
              className="input-field" 
              placeholder={role === 'admin' ? "Enter Admin ID (e.g., HOSP-001)" : "Enter Doctor ID (e.g., DOC-001)"}
              value={hospitalId}
              onChange={(e) => setHospitalId(e.target.value)}
              disabled={loading}
              required
            />
          </div>

          <div>
            <label style={{ display: 'block', marginBottom: '8px', fontSize: '0.875rem', color: 'var(--text-muted)' }}>Password</label>
            <div style={{ position: 'relative' }}>
              <input 
                type={showPassword ? 'text' : 'password'}
                className="input-field" 
                placeholder="••••••••" 
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                disabled={loading}
                required
                style={{ paddingRight: '44px' }}
              />
              <button
                type="button"
                onClick={() => setShowPassword((prev) => !prev)}
                disabled={loading}
                style={{
                  position: 'absolute',
                  right: '10px',
                  top: '50%',
                  transform: 'translateY(-50%)',
                  background: 'transparent',
                  border: 'none',
                  padding: '4px',
                  cursor: 'pointer',
                  color: 'var(--text-muted)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  height: 'calc(100% - 4px)',
                  minHeight: '30px',
                  lineHeight: 0
                }}
                aria-label={showPassword ? 'Hide password' : 'Show password'}
              >
                {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
              </button>
            </div>
          </div>

          <button 
            type="submit" 
            className="btn-primary" 
            style={{ marginTop: '8px' }}
            disabled={loading}
          >
            {loading ? '⏳ Authenticating...' : (<><Shield size={18} /> Login </>)}
          </button>
        </form>
      </div>
    </div>
  );
}