/**
 * Authentication Credentials Database
 * Hospital Admin and Specialist Doctor credentials
 */

const HOSPITALS = [
  { id: 'HOSP-001', name: 'Central Medical Hospital', region: 'North' },
  { id: 'HOSP-002', name: 'Sunrise Healthcare Centre', region: 'East' },
  { id: 'HOSP-003', name: 'Metropolitan Health Institute', region: 'West' },
  { id: 'HOSP-004', name: 'City Medical Clinic', region: 'South' }
];

const SPECIALISTS = [
  { code: 'HRT', name: 'Cardiology' },
  { code: 'NEP', name: 'Nephrology' },
  { code: 'ONC', name: 'Oncology' },
  { code: 'HEM', name: 'Haematology' }
];

export const VALID_CREDENTIALS = {
  // --- Admin Accounts ---
  'HOSP-001': {
    password: 'SecurePass123!',
    hospital_name: 'Central Medical Hospital',
    region: 'North',
    role: 'admin'
  },
  'HOSP-002': {
    password: 'HealthFirst456@',
    hospital_name: 'Sunrise Healthcare Centre',
    region: 'East',
    role: 'admin'
  },
  'HOSP-003': {
    password: 'MediCare789#',
    hospital_name: 'Metropolitan Health Institute',
    region: 'West',
    role: 'admin'
  },
  'HOSP-004': {
    password: 'CarePlus999$',
    hospital_name: 'City Medical Clinic',
    region: 'South',
    role: 'admin'
  },
  
  // Legacy / Test accounts
  'Hospital_A': { password: 'password123', hospital_name: 'Hospital Node A', region: 'Region A', role: 'admin' },
  'Hospital_B': { password: 'password456', hospital_name: 'Hospital Node B', region: 'Region B', role: 'admin' },
  'Hospital_C': { password: 'password789', hospital_name: 'Hospital Node C', region: 'Region C', role: 'admin' }
};

// Generate 16 Specialist credentials programmatically
HOSPITALS.forEach(h => {
  const hNum = h.id.split('-')[1]; // e.g., '001'
  SPECIALISTS.forEach(s => {
    const docId = `DOC-${s.code}-${hNum}`;
    VALID_CREDENTIALS[docId] = {
      password: 'doctor',
      hospital_name: h.name,
      region: h.region,
      role: 'doctor',
      hospital_id: h.id,
      specialization: s.name
    };
  });
});

/**
 * Validate hospital credentials
 */
export function validateCredentials(hospitalId, password) {
  if (!hospitalId || !password) {
    return { valid: false, message: 'ID and Password are required' };
  }

  const credentials = VALID_CREDENTIALS[hospitalId];

  if (!credentials) {
    return {
      valid: false,
      message: `ID "${hospitalId}" not found in the federated network`
    };
  }

  if (credentials.password !== password) {
    return {
      valid: false,
      message: 'Invalid Password. Please check your credentials.'
    };
  }

  return {
    valid: true,
    message: 'Authentication successful',
    hospital: {
      id: credentials.hospital_id || hospitalId,
      userId: hospitalId,
      name: credentials.hospital_name,
      region: credentials.region,
      role: credentials.role || 'admin',
      specialization: credentials.specialization || null,
      timestamp: new Date().toISOString(),
      session_id: `SESSION_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
    }
  };
}

export function saveAuthToStorage(authData) {
  localStorage.setItem('hospital_auth', JSON.stringify(authData));
  localStorage.setItem('auth_timestamp', new Date().toISOString());
}

export function getAuthFromStorage() {
  try {
    const authData = localStorage.getItem('hospital_auth');
    if (authData) {
      const parsed = JSON.parse(authData);
      const timestamp = localStorage.getItem('auth_timestamp');
      const sessionAge = new Date() - new Date(timestamp);
      const maxAge = 24 * 60 * 60 * 1000;
      if (sessionAge < maxAge) return parsed;
      clearAuthStorage();
    }
    return null;
  } catch (e) {
    return null;
  }
}

export function clearAuthStorage() {
  localStorage.removeItem('hospital_auth');
  localStorage.removeItem('auth_timestamp');
}