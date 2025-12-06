import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, NavLink, useNavigate } from 'react-router-dom';
import DriversPage from './pages/DriversPage';
import ImportPage from './pages/ImportPage';
import SchedulePage from './pages/SchedulePage';
import DashboardPage from './pages/DashboardPage';
import LoginPage from './pages/LoginPage';
import DriverSchedulePage from './pages/DriverSchedulePage';
import { api } from './services/api';

const App: React.FC = () => {
  const [user, setUser] = useState<{ user_id: string; role: string; driver_id?: string } | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    try {
      const currentUser = await api.getCurrentUser();
      setUser(currentUser);
    } catch {
      setUser(null);
    } finally {
      setLoading(false);
    }
  };

  const handleLogin = (userData: { user_id: string; role: string; driver_id?: string }) => {
    setUser(userData);
  };

  const handleLogout = async () => {
    try {
      await api.logout();
    } catch (e) {
      console.error('Logout error:', e);
    }
    setUser(null);
  };

  if (loading) {
    return (
      <div className="loading">
        <div className="spinner"></div>
        <p>Loading...</p>
      </div>
    );
  }

  if (!user) {
    return <LoginPage onLogin={handleLogin} />;
  }

  const isAdmin = user.role === 'admin';
  const isDriver = user.role === 'driver';

  return (
    <Router>
      <div style={{ display: 'flex', flexDirection: 'column', height: '100vh' }}>
        <header className="header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h1>Graceconnections - Driver Scheduling</h1>
          <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
            <span style={{ fontSize: '14px', color: '#666' }}>
              {user.user_id} ({user.role})
            </span>
            <button className="btn btn-secondary" onClick={handleLogout} style={{ padding: '6px 12px' }}>
              Logout
            </button>
          </div>
        </header>
        <nav className="nav">
          {isAdmin && (
            <>
              <NavLink to="/" className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}>
                Dashboard
              </NavLink>
              <NavLink to="/drivers" className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}>
                Drivers
              </NavLink>
              <NavLink to="/import" className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}>
                Import Clients
              </NavLink>
              <NavLink to="/schedule" className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}>
                Schedule
              </NavLink>
            </>
          )}
          {isDriver && (
            <NavLink to="/my-schedule" className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}>
              My Schedule
            </NavLink>
          )}
        </nav>
        <main style={{ flex: 1, overflow: 'auto', padding: '20px' }}>
          <Routes>
            {isAdmin && (
              <>
                <Route path="/" element={<DashboardPage />} />
                <Route path="/drivers" element={<DriversPage />} />
                <Route path="/import" element={<ImportPage />} />
                <Route path="/schedule" element={<SchedulePage />} />
              </>
            )}
            {isDriver && user.driver_id && (
              <Route path="/my-schedule" element={<DriverSchedulePage driverId={user.driver_id} />} />
            )}
            <Route path="*" element={<div>Page not found</div>} />
          </Routes>
        </main>
      </div>
    </Router>
  );
};

export default App;

