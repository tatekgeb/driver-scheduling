import React, { useState, useEffect } from 'react';
import { api, Schedule, Route, Driver } from '../services/api';
import { format } from 'date-fns';
import RouteView from '../components/RouteView';

const SchedulePage: React.FC = () => {
  const [serviceDate, setServiceDate] = useState(format(new Date(), 'yyyy-MM-dd'));
  const [loading, setLoading] = useState(false);
  const [schedule, setSchedule] = useState<Schedule | null>(null);
  const [drivers, setDrivers] = useState<Driver[]>([]);
  const [selectedRoute, setSelectedRoute] = useState<Route | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadDrivers();
  }, []);

  const loadDrivers = async () => {
    try {
      const data = await api.getDrivers();
      setDrivers(data);
    } catch (error) {
      console.error('Failed to load drivers:', error);
    }
  };

  const handleGenerateSchedule = async () => {
    if (!serviceDate) {
      alert('Please select a service date');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      
      // Get all trips for this date (empty array means get all)
      const tripIds: string[] = [];
      
      const newSchedule = await api.generateSchedule(serviceDate, tripIds);
      setSchedule(newSchedule);
    } catch (error: any) {
      setError(error.message || 'Failed to generate schedule');
    } finally {
      setLoading(false);
    }
  };

  const handleExport = async () => {
    if (!schedule) {
      alert('No schedule to export');
      return;
    }

    try {
      const blob = await api.exportScheduleToCSV(schedule.schedule_id);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `schedule_${serviceDate}.csv`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error: any) {
      alert(`Export failed: ${error.message}`);
    }
  };

  const getDriverName = (driverId: string) => {
    const driver = drivers.find(d => d.driver_id === driverId);
    return driver ? driver.name : driverId;
  };

  return (
    <div className="container">
      <div className="card">
        <div className="card-header">
          <h2 className="card-title">Schedule Management</h2>
          <div style={{ display: 'flex', gap: '12px' }}>
            <input
              type="date"
              className="form-input"
              value={serviceDate}
              onChange={(e) => setServiceDate(e.target.value)}
              style={{ maxWidth: '200px' }}
            />
            <button
              className="btn btn-primary"
              onClick={handleGenerateSchedule}
              disabled={loading}
            >
              {loading ? 'Generating...' : 'Generate Schedule'}
            </button>
            {schedule && (
              <button
                className="btn btn-success"
                onClick={handleExport}
              >
                Export CSV
              </button>
            )}
          </div>
        </div>

        {error && (
          <div className="alert alert-error">
            {error}
          </div>
        )}

        {loading && (
          <div className="loading">
            <div className="spinner"></div>
            <p>Generating optimized schedule...</p>
          </div>
        )}

        {schedule && (
          <>
            <div style={{ marginBottom: '20px', padding: '16px', background: '#f8f9fa', borderRadius: '8px' }}>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '20px' }}>
                <div>
                  <div style={{ fontSize: '12px', color: '#666' }}>Service Date</div>
                  <div style={{ fontSize: '18px', fontWeight: '600' }}>
                    {format(new Date(schedule.service_date), 'MMM dd, yyyy')}
                  </div>
                </div>
                <div>
                  <div style={{ fontSize: '12px', color: '#666' }}>Total Routes</div>
                  <div style={{ fontSize: '18px', fontWeight: '600' }}>{schedule.routes.length}</div>
                </div>
                <div>
                  <div style={{ fontSize: '12px', color: '#666' }}>Total Clients</div>
                  <div style={{ fontSize: '18px', fontWeight: '600' }}>
                    {schedule.routes.reduce((sum, r) => sum + r.total_clients, 0)}
                  </div>
                </div>
                <div>
                  <div style={{ fontSize: '12px', color: '#666' }}>Unassigned</div>
                  <div style={{ fontSize: '18px', fontWeight: '600', color: schedule.unassigned_trips.length > 0 ? '#ef4444' : '#10b981' }}>
                    {schedule.unassigned_trips.length}
                  </div>
                </div>
              </div>
            </div>

            {schedule.unassigned_trips.length > 0 && (
              <div className="alert alert-warning" style={{ marginBottom: '20px' }}>
                <strong>Warning:</strong> {schedule.unassigned_trips.length} trip(s) could not be assigned.
                This may be due to time constraints, driver availability, or insufficient drivers.
              </div>
            )}

            <div style={{ display: 'grid', gap: '20px' }}>
              {schedule.routes.map(route => (
                <div key={route.route_id} className="card">
                  <div className="card-header">
                    <div>
                      <h3 className="card-title">{getDriverName(route.driver_id)}</h3>
                      <div style={{ fontSize: '14px', color: '#666', marginTop: '4px' }}>
                        {format(new Date(route.start_time), 'HH:mm')} - {format(new Date(route.end_time), 'HH:mm')}
                        {' • '}
                        {route.total_clients} clients • {route.total_stops} stops
                        {' • '}
                        {route.total_drive_time_minutes.toFixed(1)} min • {route.total_drive_distance_miles.toFixed(1)} mi
                      </div>
                    </div>
                    <button
                      className="btn btn-secondary"
                      onClick={() => setSelectedRoute(selectedRoute?.route_id === route.route_id ? null : route)}
                    >
                      {selectedRoute?.route_id === route.route_id ? 'Hide' : 'View'} Details
                    </button>
                  </div>

                  {selectedRoute?.route_id === route.route_id && (
                    <RouteView route={route} />
                  )}
                </div>
              ))}
            </div>
          </>
        )}

        {!schedule && !loading && (
          <div className="text-center" style={{ padding: '40px' }}>
            <p style={{ color: '#666', marginBottom: '20px' }}>
              Select a service date and click "Generate Schedule" to create an optimized schedule.
            </p>
            <p style={{ fontSize: '14px', color: '#999' }}>
              Make sure you have imported client data and added drivers first.
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default SchedulePage;

