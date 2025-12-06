import React, { useEffect, useState } from 'react';
import { api, Driver } from '../services/api';
import DriverForm from '../components/DriverForm';

const DriversPage: React.FC = () => {
  const [drivers, setDrivers] = useState<Driver[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editingDriver, setEditingDriver] = useState<Driver | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadDrivers();
  }, []);

  const loadDrivers = async () => {
    try {
      setLoading(true);
      const data = await api.getDrivers();
      setDrivers(data);
    } catch (error: any) {
      setError(error.message || 'Failed to load drivers');
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = () => {
    setEditingDriver(null);
    setShowForm(true);
  };

  const handleEdit = (driver: Driver) => {
    setEditingDriver(driver);
    setShowForm(true);
  };

  const handleDelete = async (driverId: string) => {
    if (!confirm('Are you sure you want to delete this driver?')) {
      return;
    }

    try {
      await api.deleteDriver(driverId);
      await loadDrivers();
    } catch (error: any) {
      setError(error.message || 'Failed to delete driver');
    }
  };

  const handleFormSubmit = async (driver: Driver) => {
    try {
      if (editingDriver) {
        await api.updateDriver(editingDriver.driver_id, driver);
      } else {
        await api.createDriver(driver);
      }
      setShowForm(false);
      setEditingDriver(null);
      await loadDrivers();
    } catch (error: any) {
      setError(error.message || 'Failed to save driver');
    }
  };

  const handleFormCancel = () => {
    setShowForm(false);
    setEditingDriver(null);
  };

  if (loading) {
    return (
      <div className="loading">
        <div className="spinner"></div>
        <p>Loading drivers...</p>
      </div>
    );
  }

  return (
    <div className="container">
      <div className="card">
        <div className="card-header">
          <h2 className="card-title">Driver Management</h2>
          <button className="btn btn-primary" onClick={handleCreate}>
            + Add Driver
          </button>
        </div>

        {error && (
          <div className="alert alert-error">
            {error}
          </div>
        )}

        {showForm && (
          <DriverForm
            driver={editingDriver}
            onSubmit={handleFormSubmit}
            onCancel={handleFormCancel}
          />
        )}

        {drivers.length === 0 ? (
          <div className="text-center" style={{ padding: '40px' }}>
            <p style={{ color: '#666', marginBottom: '20px' }}>No drivers found. Add your first driver to get started.</p>
            <button className="btn btn-primary" onClick={handleCreate}>
              Add Driver
            </button>
          </div>
        ) : (
          <table className="table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Status</th>
                <th>Home Address</th>
                <th>Phone</th>
                <th>Service Days</th>
                <th>Hours</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {drivers.map(driver => (
                <tr key={driver.driver_id}>
                  <td>{driver.name}</td>
                  <td>
                    <span className={`badge ${driver.active ? 'badge-success' : 'badge-danger'}`}>
                      {driver.active ? 'Active' : 'Inactive'}
                    </span>
                  </td>
                  <td>
                    {driver.home_address.full_address || 
                     `${driver.home_address.street_number} ${driver.home_address.street}, ${driver.home_address.city}`}
                  </td>
                  <td>{driver.phone || '-'}</td>
                  <td>{driver.service_days.join(', ') || 'None'}</td>
                  <td>
                    {driver.daily_start_time && driver.daily_end_time
                      ? `${driver.daily_start_time} - ${driver.daily_end_time}`
                      : 'Not set'}
                  </td>
                  <td>
                    <div style={{ display: 'flex', gap: '8px' }}>
                      <button
                        className="btn btn-secondary"
                        style={{ padding: '6px 12px', fontSize: '12px' }}
                        onClick={() => handleEdit(driver)}
                      >
                        Edit
                      </button>
                      <button
                        className="btn btn-danger"
                        style={{ padding: '6px 12px', fontSize: '12px' }}
                        onClick={() => handleDelete(driver.driver_id)}
                      >
                        Delete
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
};

export default DriversPage;

