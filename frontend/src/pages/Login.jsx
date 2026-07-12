import React, { useState, useContext } from 'react';
import { Link } from 'react-router-dom';
import { Package } from 'lucide-react';
import { AuthContext } from '../context/AuthContext';

const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const { login } = useContext(AuthContext);

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await login(email, password);
    } catch (err) {
      setError('Invalid email or password');
    }
  };

  return (
    <div className="app-container" style={{justifyContent: 'center', alignItems: 'center'}}>
      <div className="glass-card" style={{width: '100%', maxWidth: '400px', padding: '2.5rem'}}>
        <div style={{display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.75rem', marginBottom: '2rem'}}>
          <Package size={32} color="#6366f1" />
          <h1 style={{fontSize: '1.75rem', fontWeight: '700'}}>AssetFlow</h1>
        </div>
        
        <h2 style={{textAlign: 'center', marginBottom: '1.5rem', fontWeight: '500'}}>Welcome Back</h2>
        
        {error && <div style={{color: 'var(--danger)', marginBottom: '1rem', textAlign: 'center', padding: '10px', background: 'rgba(239, 68, 68, 0.1)', borderRadius: '8px'}}>{error}</div>}

        <form onSubmit={handleSubmit} style={{display: 'flex', flexDirection: 'column', gap: '1rem'}}>
          <div>
            <label style={{display: 'block', marginBottom: '0.5rem', color: 'var(--text-muted)'}}>Work Email</label>
            <input 
              type="email" 
              required
              style={inputStyle}
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
          </div>
          <div>
            <label style={{display: 'block', marginBottom: '0.5rem', color: 'var(--text-muted)'}}>Password</label>
            <input 
              type="password" 
              required
              style={inputStyle}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </div>
          
          <button type="submit" style={buttonStyle}>Log In</button>
        </form>

        <p style={{textAlign: 'center', marginTop: '1.5rem', color: 'var(--text-muted)'}}>
          Don't have an account? <Link to="/signup" style={{color: 'var(--primary)', textDecoration: 'none'}}>Sign up</Link>
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

export default Login;
