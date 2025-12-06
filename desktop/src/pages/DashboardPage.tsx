import React, { useEffect, useState } from 'react';
import { api, Driver, Schedule } from '../services/api';
import { format } from 'date-fns';

const DashboardPage: React.FC = () => {
  const [drivers, setDrivers] = useState<Driver[]>([]);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({
    totalDrivers: 0,
    activeDrivers: 0,
    recentSchedules: 0,
  });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const driversData = await api.getDrivers();
      setDrivers(driversData);
      setStats({
        totalDrivers: driversData.length,
        activeDrivers: driversData.filter(d => d.active).length,
        recentSchedules: 0, // TODO: Load from storage
      });
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="loading">
        <div className="spinner"></div>
        <p>Loading dashboard...</p>
      </div>
    );
  }

  return (
    <div className="container">
      <h2 style={{ marginBottom: '24px' }}>Dashboard</h2>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '20px', marginBottom: '30px' }}>
        <div className="card">
          <h3 className="card-title">Total Drivers</h3>
          <div style={{ fontSize: '32px', fontWeight: 'bold', color: '#667eea' }}>
            {stats.totalDrivers}
          </div>
        </div>

        <div className="card">
          <h3 className="card-title">Active Drivers</h3>
          <div style={{ fontSize: '32px', fontWeight: 'bold', color: '#10b981' }}>
            {stats.activeDrivers}
          </div>
        </div>

        <div className="card">
          <h3 className="card-title">Recent Schedules</h3>
          <div style={{ fontSize: '32px', fontWeight: 'bold', color: '#f59e0b' }}>
            {stats.recentSchedules}
          </div>
        </div>
      </div>

      <div className="card">
        <div className="card-header">
          <h3 className="card-title">Quick Actions</h3>
        </div>
        <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
          <button className="btn btn-primary" onClick={() => window.location.hash = '#/drivers'}>
            Manage Drivers
          </button>
          <button className="btn btn-primary" onClick={() => window.location.hash = '#/import'}>
            Import Client Data
          </button>
          <button className="btn btn-primary" onClick={() => window.location.hash = '#/schedule'}>
            Generate Schedule
          </button>
        </div>
      </div>

      {drivers.length > 0 && (
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">Recent Drivers</h3>
          </div>
          <table className="table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Status</th>
                <th>Home Address</th>
                <th>Service Days</th>
                <th>Hours</th>
              </tr>
            </thead>
            <tbody>
              {drivers.slice(0, 5).map(driver => (
                <tr key={driver.driver_id}>
                  <td>{driver.name}</td>
                  <td>
                    <span className={`badge ${driver.active ? 'badge-success' : 'badge-danger'}`}>
                      {driver.active ? 'Active' : 'Inactive'}
                    </span>
                  </td>
                  <td>{driver.home_address.full_address || `${driver.home_address.street_number} ${driver.home_address.street}, ${driver.home_address.city}`}</td>
                  <td>{driver.service_days.join(', ') || 'None'}</td>
                  <td>
                    {driver.daily_start_time && driver.daily_end_time
                      ? `${driver.daily_start_time} - ${driver.daily_end_time}`
                      : 'Not set'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default DashboardPage;

