import React, { useState, useEffect } from 'react';
import { api, Route } from '../services/api';
import { format } from 'date-fns';

interface DriverSchedulePageProps {
  driverId: string;
}

const DriverSchedulePage: React.FC<DriverSchedulePageProps> = ({ driverId }) => {
  const [serviceDate, setServiceDate] = useState(format(new Date(), 'yyyy-MM-dd'));
  const [route, setRoute] = useState<Route | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [schedules, setSchedules] = useState<any[]>([]);

  useEffect(() => {
    loadSchedules();
  }, [serviceDate]);

  const loadSchedules = async () => {
    try {
      setLoading(true);
      setError(null);
      const scheduleList = await api.listSchedules(serviceDate);
      setSchedules(scheduleList);
      
      // Find route for this driver
      for (const schedule of scheduleList) {
        const driverRoute = schedule.routes.find((r: Route) => r.driver_id === driverId);
        if (driverRoute) {
          setRoute(driverRoute);
          return;
        }
      }
      setRoute(null);
    } catch (err: any) {
      setError(err.message || 'Failed to load schedule');
    } finally {
      setLoading(false);
    }
  };

  const handlePrint = () => {
    window.print();
  };

  if (loading) {
    return (
      <div className="loading">
        <div className="spinner"></div>
        <p>Loading schedule...</p>
      </div>
    );
  }

  return (
    <div className="container">
      <div className="card">
        <div className="card-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <h2 className="card-title">My Schedule</h2>
            <div style={{ marginTop: '8px' }}>
              <input
                type="date"
                className="form-input"
                value={serviceDate}
                onChange={(e) => setServiceDate(e.target.value)}
                style={{ maxWidth: '200px' }}
              />
            </div>
          </div>
          {route && (
            <button className="btn btn-primary" onClick={handlePrint}>
              🖨️ Print Schedule
            </button>
          )}
        </div>

        {error && (
          <div className="alert alert-error">
            {error}
          </div>
        )}

        {!route && !loading && (
          <div className="text-center" style={{ padding: '40px' }}>
            <p style={{ color: '#666' }}>No schedule found for {format(new Date(serviceDate), 'MMM dd, yyyy')}.</p>
            <p style={{ fontSize: '14px', color: '#999', marginTop: '10px' }}>
              Please contact dispatch if you believe this is an error.
            </p>
          </div>
        )}

        {route && (
          <div className="print-schedule">
            {/* Print-only header with logo */}
            <div className="print-header" style={{ display: 'none' }}>
              <div style={{ textAlign: 'center', marginBottom: '30px', borderBottom: '2px solid #333', paddingBottom: '20px' }}>
                <h1 style={{ fontSize: '36px', marginBottom: '10px', fontWeight: 'bold', color: '#333' }}>Graceconnections</h1>
                <h2 style={{ fontSize: '22px', color: '#666', fontWeight: 'normal', marginTop: '5px' }}>Driver Schedule</h2>
                <div style={{ fontSize: '14px', color: '#999', marginTop: '10px' }}>
                  {format(new Date(route.service_date), 'MMMM dd, yyyy')}
                </div>
              </div>
            </div>

            <div style={{ marginBottom: '30px' }}>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '20px', marginBottom: '20px' }}>
                <div>
                  <div style={{ fontSize: '12px', color: '#666' }}>Service Date</div>
                  <div style={{ fontSize: '18px', fontWeight: '600' }}>
                    {format(new Date(route.service_date), 'MMM dd, yyyy')}
                  </div>
                </div>
                <div>
                  <div style={{ fontSize: '12px', color: '#666' }}>Total Clients</div>
                  <div style={{ fontSize: '18px', fontWeight: '600' }}>{route.total_clients}</div>
                </div>
                <div>
                  <div style={{ fontSize: '12px', color: '#666' }}>Total Stops</div>
                  <div style={{ fontSize: '18px', fontWeight: '600' }}>{route.total_stops}</div>
                </div>
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '20px' }}>
                <div>
                  <div style={{ fontSize: '12px', color: '#666' }}>Start Time</div>
                  <div style={{ fontSize: '18px', fontWeight: '600' }}>
                    {format(new Date(route.start_time), 'HH:mm')}
                  </div>
                </div>
                <div>
                  <div style={{ fontSize: '12px', color: '#666' }}>End Time</div>
                  <div style={{ fontSize: '18px', fontWeight: '600' }}>
                    {format(new Date(route.end_time), 'HH:mm')}
                  </div>
                </div>
              </div>
            </div>

            <table className="table" style={{ marginTop: '20px' }}>
              <thead>
                <tr>
                  <th>Stop #</th>
                  <th>Action</th>
                  <th>Passenger</th>
                  <th>Address</th>
                  <th>Arrival</th>
                  <th>Departure</th>
                  <th>Appointment</th>
                  <th>Notes</th>
                </tr>
              </thead>
              <tbody>
                {route.stops.map((stop) => (
                  <tr key={stop.stop_number}>
                    <td>{stop.stop_number}</td>
                    <td>
                      <span className={`badge ${stop.action === 'pickup' ? 'badge-info' : 'badge-success'}`}>
                        {stop.action.toUpperCase()}
                      </span>
                    </td>
                    <td>{stop.client_trip.passenger_name}</td>
                    <td>
                      {stop.address.street_number} {stop.address.street}, {stop.address.city}
                    </td>
                    <td>{format(new Date(stop.planned_arrival_time), 'HH:mm')}</td>
                    <td>{format(new Date(stop.planned_departure_time), 'HH:mm')}</td>
                    <td>
                      {stop.appointment_time
                        ? format(new Date(stop.appointment_time), 'HH:mm')
                        : '-'}
                    </td>
                    <td>{stop.notes || '-'}</td>
                  </tr>
                ))}
              </tbody>
            </table>

            <div style={{ marginTop: '20px', padding: '16px', background: '#f8f9fa', borderRadius: '8px' }}>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '20px' }}>
                <div>
                  <div style={{ fontSize: '12px', color: '#666' }}>Total Drive Time</div>
                  <div style={{ fontSize: '16px', fontWeight: '600' }}>
                    {route.total_drive_time_minutes.toFixed(1)} minutes
                  </div>
                </div>
                <div>
                  <div style={{ fontSize: '12px', color: '#666' }}>Total Distance</div>
                  <div style={{ fontSize: '16px', fontWeight: '600' }}>
                    {route.total_drive_distance_miles.toFixed(1)} miles
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      <style>{`
        @media print {
          @page {
            margin: 0.5in;
          }
          
          .card-header button,
          .nav,
          .header {
            display: none !important;
          }
          
          .print-header {
            display: block !important;
            page-break-after: avoid;
          }
          
          .container {
            max-width: 100%;
            padding: 0;
          }
          
          .card {
            box-shadow: none;
            border: none;
            page-break-inside: avoid;
          }
          
          .table {
            font-size: 11px;
            border-collapse: collapse;
            width: 100%;
          }
          
          .table th,
          .table td {
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
          }
          
          .table th {
            background-color: #f5f5f5;
            font-weight: bold;
          }
          
          .badge {
            padding: 4px 8px;
            font-size: 10px;
            border: 1px solid #ccc;
          }
          
          .print-schedule {
            page-break-inside: avoid;
          }
        }
      `}</style>
    </div>
  );
};

export default DriverSchedulePage;

