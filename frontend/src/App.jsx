import React, { useState, useEffect, useContext } from 'react';
import { BrowserRouter, Routes, Route, Link, useLocation, Navigate } from 'react-router-dom';
import axios from 'axios';
import { 
  LayoutDashboard, 
  Package, 
  Wrench, 
  TrendingUp, 
  AlertTriangle,
  LogOut,
  User as UserIcon,
  Calendar,
  ShieldCheck,
  Activity
} from 'lucide-react';

import { AuthProvider, AuthContext } from './context/AuthContext';
import Login from './pages/Login';
import Signup from './pages/Signup';

const API_BASE = 'http://localhost:8000/api';

const ProtectedRoute = ({ children }) => {
  const { user } = useContext(AuthContext);
  if (!user) {
    return <Navigate to="/login" replace />;
  }
  return children;
};

const Sidebar = () => {
  const location = useLocation();
  const { user, logout } = useContext(AuthContext);
  
  const navItems = [
    { path: '/', label: 'Dashboard', icon: <LayoutDashboard size={20} /> },
    { path: '/assets', label: 'Assets', icon: <Package size={20} /> },
    { path: '/maintenance', label: 'Maintenance', icon: <Wrench size={20} /> },
    { path: '/predictions', label: 'AI Predictions', icon: <AlertTriangle size={20} /> },
    { path: '/forecast', label: 'Demand Forecast', icon: <TrendingUp size={20} /> },
    { path: '/bookings', label: 'Resource Booking', icon: <Calendar size={20} /> },
    { path: '/audits', label: 'Compliance Audits', icon: <ShieldCheck size={20} /> },
    { path: '/activity', label: 'Activity Logs', icon: <Activity size={20} /> },
  ];

  return (
    <div className="sidebar" style={{display: 'flex', flexDirection: 'column', height: '100vh', overflowY: 'auto'}}>
      <div>
        <div className="sidebar-logo" style={{marginBottom: '2rem'}}>
          <Package size={28} color="#6366f1" />
          <span>AssetFlow</span>
        </div>
        {navItems.map((item) => (
          <Link
            key={item.path}
            to={item.path}
            className={`nav-item ${location.pathname === item.path ? 'active' : ''}`}
          >
            {item.icon}
            {item.label}
          </Link>
        ))}
      </div>
      
      <div style={{marginTop: 'auto', paddingTop: '2rem'}}>
        <div style={{padding: '1rem', borderTop: '1px solid var(--border)', display: 'flex', alignItems: 'center', gap: '0.75rem'}}>
          <div style={{background: 'var(--primary)', borderRadius: '50%', padding: '0.5rem', display: 'flex'}}>
            <UserIcon size={16} />
          </div>
          <div style={{flex: 1, overflow: 'hidden'}}>
            <div style={{fontWeight: 500, fontSize: '0.9rem', whiteSpace: 'nowrap', textOverflow: 'ellipsis', overflow: 'hidden'}}>{user.name}</div>
            <div style={{fontSize: '0.75rem', color: 'var(--text-muted)'}}>{user.role}</div>
          </div>
        </div>
        <button 
          onClick={logout}
          className="nav-item" 
          style={{width: '100%', border: 'none', background: 'transparent', textAlign: 'left', color: 'var(--danger)', marginTop: '0.5rem'}}
        >
          <LogOut size={20} />
          Log Out
        </button>
      </div>
    </div>
  );
};

// --- PAGES ---

const Dashboard = () => {
  const [summary, setSummary] = useState(null);

  useEffect(() => {
    axios.get(`${API_BASE}/dashboard/summary`).then(res => setSummary(res.data));
  }, []);

  if (!summary) return <div className="main-content">Loading...</div>;

  return (
    <div className="main-content">
      <div className="header">
        <h1>Master Dashboard</h1>
      </div>
      
      <div className="dashboard-grid">
        <div className="glass-card stat-card">
          <div className="stat-header">
            <span>Total Assets</span>
            <Package size={20} className="text-muted" />
          </div>
          <div className="stat-value">{summary.total_assets}</div>
        </div>
        <div className="glass-card stat-card">
          <div className="stat-header">
            <span>Active Assets</span>
            <div className="badge active">Operational</div>
          </div>
          <div className="stat-value">{summary.active_assets}</div>
        </div>
        <div className="glass-card stat-card">
          <div className="stat-header">
            <span>Pending Maintenance</span>
            <Wrench size={20} className="text-muted" />
          </div>
          <div className="stat-value">{summary.pending_maintenance}</div>
        </div>
        <div className="glass-card stat-card">
          <div className="stat-header">
            <span>Critical AI Alerts</span>
            <div className="badge critical">Urgent</div>
          </div>
          <div className="stat-value" style={{color: 'var(--danger)'}}>{summary.high_risk_assets}</div>
        </div>
      </div>

      <div className="dashboard-grid" style={{gridTemplateColumns: '1fr 1fr'}}>
        <div className="glass-card">
          <h3 style={{marginBottom: '1rem', fontWeight: 500}}>System Status</h3>
          <p style={{color: 'var(--text-muted)'}}>All AI prediction models are online. Database connection stable.</p>
        </div>
      </div>
    </div>
  );
};

const Assets = () => {
  const [assets, setAssets] = useState([]);

  useEffect(() => {
    axios.get(`${API_BASE}/assets`).then(res => setAssets(res.data));
  }, []);

  return (
    <div className="main-content">
      <div className="header">
        <h1>Assets Directory</h1>
      </div>
      <div className="glass-card table-container">
        <table>
          <thead>
            <tr>
              <th>Code</th>
              <th>Name</th>
              <th>Category</th>
              <th>Location</th>
              <th>Health</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {assets.map(asset => (
              <tr key={asset.id}>
                <td><strong>{asset.asset_code}</strong></td>
                <td>{asset.name}</td>
                <td>{asset.category}</td>
                <td>{asset.current_location}</td>
                <td style={{width: '150px'}}>
                  <div className="progress-bg">
                    <div className={`progress-fill ${asset.health_score > 70 ? 'good' : asset.health_score > 40 ? 'warning' : 'danger'}`} 
                         style={{width: `${asset.health_score}%`}}></div>
                  </div>
                </td>
                <td><span className={`badge ${asset.state}`}>{asset.state}</span></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

const Predictions = () => {
  const [predictions, setPredictions] = useState([]);
  
  useEffect(() => {
    axios.get(`${API_BASE}/predictions`).then(res => setPredictions(res.data));
  }, []);

  return (
    <div className="main-content">
      <div className="header">
        <h1>AI Predictive Maintenance</h1>
      </div>
      <div className="dashboard-grid">
        {predictions.map(pred => (
          <div key={pred.id} className="glass-card">
            <div style={{display: 'flex', justifyContent: 'space-between', marginBottom: '1rem'}}>
              <strong>Asset ID: {pred.asset_id}</strong>
              <span className={`badge ${pred.risk_level}`}>{pred.risk_level} Risk</span>
            </div>
            <div style={{color: 'var(--text-muted)', fontSize: '0.9rem', marginBottom: '0.5rem'}}>
              Predicted Failure: {pred.predicted_failure_date}
            </div>
            <div style={{color: 'var(--text-muted)', fontSize: '0.9rem', marginBottom: '1rem'}}>
              AI Confidence: {(pred.confidence * 100).toFixed(1)}%
            </div>
            <p style={{fontSize: '0.85rem', lineHeight: '1.4', padding: '0.75rem', background: 'rgba(0,0,0,0.2)', borderRadius: '8px'}}>
              {pred.factors}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
};

const Bookings = () => {
  const [bookings, setBookings] = useState([]);
  useEffect(() => { axios.get(`${API_BASE}/bookings`).then(res => setBookings(res.data)); }, []);
  return (
    <div className="main-content">
      <div className="header"><h1>Shared Resource Bookings</h1></div>
      <div className="dashboard-grid">
        {bookings.map(b => (
          <div key={b.id} className="glass-card">
            <h3>{b.resource_name}</h3>
            <p style={{color: 'var(--text-muted)', marginTop: '0.5rem'}}>Booked by: {b.booked_by}</p>
            <p style={{fontSize: '0.85rem', marginTop: '1rem'}}>Starts: {new Date(b.start_time).toLocaleString()}</p>
            <p style={{fontSize: '0.85rem'}}>Ends: {new Date(b.end_time).toLocaleString()}</p>
          </div>
        ))}
      </div>
    </div>
  );
};

const Audits = () => {
  const [audits, setAudits] = useState([]);
  useEffect(() => { axios.get(`${API_BASE}/audits`).then(res => setAudits(res.data)); }, []);
  return (
    <div className="main-content">
      <div className="header"><h1>Compliance Audits</h1></div>
      <div className="glass-card table-container">
        <table>
          <thead>
            <tr><th>Title</th><th>Auditor</th><th>Date</th><th>Status</th></tr>
          </thead>
          <tbody>
            {audits.map(a => (
              <tr key={a.id}>
                <td><strong>{a.title}</strong></td>
                <td>{a.auditor_name}</td>
                <td>{a.audit_date}</td>
                <td><span className={`badge ${a.status === 'passed' ? 'good' : a.status === 'failed' ? 'critical' : 'active'}`}>{a.status}</span></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

const ActivityLogs = () => {
  const [logs, setLogs] = useState([]);
  useEffect(() => { axios.get(`${API_BASE}/activity`).then(res => setLogs(res.data)); }, []);
  return (
    <div className="main-content">
      <div className="header"><h1>Activity & Audit Logs</h1></div>
      <div className="glass-card table-container">
        <table>
          <thead>
            <tr><th>Timestamp</th><th>User</th><th>Action</th><th>Target</th></tr>
          </thead>
          <tbody>
            {logs.map(log => (
              <tr key={log.id}>
                <td>{new Date(log.timestamp).toLocaleString()}</td>
                <td>{log.user_email}</td>
                <td><span className="badge active">{log.action}</span></td>
                <td>{log.target}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

// --- APP ROOT ---

const AppContent = () => {
  const { user } = useContext(AuthContext);
  
  if (!user) {
    return (
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/signup" element={<Signup />} />
        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    );
  }

  return (
    <div className="app-container">
      <Sidebar />
      <Routes>
        <Route path="/" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
        <Route path="/assets" element={<ProtectedRoute><Assets /></ProtectedRoute>} />
        <Route path="/maintenance" element={<ProtectedRoute><div className="main-content"><h1>Maintenance Requests</h1></div></ProtectedRoute>} />
        <Route path="/predictions" element={<ProtectedRoute><Predictions /></ProtectedRoute>} />
        <Route path="/forecast" element={<ProtectedRoute><div className="main-content"><h1>Demand Forecasts</h1></div></ProtectedRoute>} />
        <Route path="/bookings" element={<ProtectedRoute><Bookings /></ProtectedRoute>} />
        <Route path="/audits" element={<ProtectedRoute><Audits /></ProtectedRoute>} />
        <Route path="/activity" element={<ProtectedRoute><ActivityLogs /></ProtectedRoute>} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </div>
  );
};

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppContent />
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;
