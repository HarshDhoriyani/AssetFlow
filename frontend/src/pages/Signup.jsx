import React, { useState, useContext } from 'react';
import { Link } from 'react-router-dom';
import { Package } from 'lucide-react';
import { AuthContext } from '../context/AuthContext';

const Signup = () => {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    company_name: '',
    role: 'Admin'
  });
  const [error, setError] = useState('');
  const { signup } = useContext(AuthContext);

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await signup(formData);
    } catch (err) {
      setError(err.response?.data?.detail || 'An error occurred during signup');
    }
  };

  return (
    <div className="app-container" style={{justifyContent: 'center', alignItems: 'center'}}>
      <div className="glass-card" style={{width: '100%', maxWidth: '450px', padding: '2.5rem'}}>
        <div style={{display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.75rem', marginBottom: '2rem'}}>
          <Package size={32} color="#6366f1" />
          <h1 style={{fontSize: '1.75rem', fontWeight: '700'}}>AssetFlow</h1>
        </div>
        
        <h2 style={{textAlign: 'center', marginBottom: '1.5rem', fontWeight: '500'}}>Create an Account</h2>
        
        {error && <div style={{color: 'var(--danger)', marginBottom: '1rem', textAlign: 'center', padding: '10px', background: 'rgba(239, 68, 68, 0.1)', borderRadius: '8px'}}>{error}</div>}

        <form onSubmit={handleSubmit} style={{display: 'flex', flexDirection: 'column', gap: '1rem'}}>
          <div>
            <label style={{display: 'block', marginBottom: '0.5rem', color: 'var(--text-muted)'}}>Full Name</label>
            <input 
              type="text" 
              required
              style={inputStyle}
              value={formData.name}
              onChange={(e) => setFormData({...formData, name: e.target.value})}
            />
          </div>
          <div>
            <label style={{display: 'block', marginBottom: '0.5rem', color: 'var(--text-muted)'}}>Work Email</label>
            <input 
              type="email" 
              required
              style={inputStyle}
              value={formData.email}
              onChange={(e) => setFormData({...formData, email: e.target.value})}
            />
          </div>
          <div>
            <label style={{display: 'block', marginBottom: '0.5rem', color: 'var(--text-muted)'}}>Password</label>
            <input 
              type="password" 
              required
              style={inputStyle}
              value={formData.password}
              onChange={(e) => setFormData({...formData, password: e.target.value})}
            />
          </div>
          <div>
            <label style={{display: 'block', marginBottom: '0.5rem', color: 'var(--text-muted)'}}>Company Name</label>
            <input 
              type="text" 
              required
              style={inputStyle}
              value={formData.company_name}
              onChange={(e) => setFormData({...formData, company_name: e.target.value})}
            />
          </div>
          <div>
            <label style={{display: 'block', marginBottom: '0.5rem', color: 'var(--text-muted)'}}>Role</label>
            <select 
              style={inputStyle}
              value={formData.role}
              onChange={(e) => setFormData({...formData, role: e.target.value})}
            >
              <option value="Admin">Admin</option>
              <option value="Manager">Facility Manager</option>
              <option value="Technician">Technician</option>
            </select>
          </div>
          
          <button type="submit" style={buttonStyle}>Sign Up</button>
        </form>

        <p style={{textAlign: 'center', marginTop: '1.5rem', color: 'var(--text-muted)'}}>
          Already have an account? <Link to="/login" style={{color: 'var(--primary)', textDecoration: 'none'}}>Log in</Link>
        </p>
      </div>
    </div>
  );
};

const inputStyle = {
  width: '100%',
  padding: '0.75rem',
  borderRadius: '8px',
  border: '1px solid var(--border)',
  background: 'rgba(0, 0, 0, 0.2)',
  color: 'white',
  outline: 'none',
  fontSize: '1rem'
};

const buttonStyle = {
  width: '100%',
  padding: '0.875rem',
  borderRadius: '8px',
  border: 'none',
  background: 'var(--primary)',
  color: 'white',
  fontSize: '1rem',
  fontWeight: '600',
  cursor: 'pointer',
  marginTop: '0.5rem',
  transition: 'background 0.3s'
};

export default Signup;
