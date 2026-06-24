import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import { getAuthFromStorage, clearAuthStorage } from './auth';
import './index.css';

function App() {
  const [hospitalAuth, setHospitalAuth] = useState(null);
  const [loading, setLoading] = useState(true);

  // Restore authentication from localStorage on component mount
  useEffect(() => {
    const savedAuth = getAuthFromStorage();
    if (savedAuth) {
      setHospitalAuth(savedAuth);
    }
    setLoading(false);
  }, []);

  const handleLogin = (auth) => {
    setHospitalAuth(auth);
  };

  const handleLogout = () => {
    clearAuthStorage();
    setHospitalAuth(null);
  };

  // Show loading state while checking authentication
  if (loading) {
    return (
      <div style={{ 
        minHeight: '100vh', 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'center',
        background: 'linear-gradient(135deg, #0f172a 0%, #1e293b 100%)'
      }}>
        <div style={{ textAlign: 'center' }}>
          <div style={{ fontSize: '24px', color: '#0ea5e9', marginBottom: '16px' }}>⏳</div>
          <p style={{ color: '#94a3b8' }}>Initializing Federated HealthNet...</p>
        </div>
      </div>
    );
  }

  return (
    <BrowserRouter>
      <Routes>
        <Route 
          path="/login" 
          element={hospitalAuth ? <Navigate to="/dashboard" replace /> : <Login onLogin={handleLogin} />} 
        />
        <Route 
          path="/dashboard" 
          element={hospitalAuth ? <Dashboard hospital={hospitalAuth} onLogout={handleLogout} /> : <Navigate to="/login" />} 
        />
        <Route path="*" element={<Navigate to="/login" />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;