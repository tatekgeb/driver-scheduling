import React, { useState } from 'react';
import { api, ClientTrip, ValidationError } from '../services/api';
import { format } from 'date-fns';

const ImportPage: React.FC = () => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [serviceDate, setServiceDate] = useState(format(new Date(), 'yyyy-MM-dd'));
  const [loading, setLoading] = useState(false);
  const [trips, setTrips] = useState<ClientTrip[]>([]);
  const [errors, setErrors] = useState<ValidationError[]>([]);
  const [success, setSuccess] = useState(false);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setSelectedFile(file);
    }
  };

  const handleImport = async () => {
    if (!selectedFile) {
      alert('Please select a CSV file');
      return;
    }

    try {
      setLoading(true);
      setSuccess(false);
      setErrors([]);
      setTrips([]);

      const result = await api.importCSV(selectedFile, serviceDate);
      setTrips(result.trips);
      setErrors(result.errors);
      setSuccess(true);
    } catch (error: any) {
      alert(`Import failed: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <div className="card">
        <div className="card-header">
          <h2 className="card-title">Import Client Data</h2>
        </div>

        <div className="form-group">
          <label className="form-label">Service Date *</label>
          <input
            type="date"
            className="form-input"
            value={serviceDate}
            onChange={(e) => setServiceDate(e.target.value)}
            required
            style={{ maxWidth: '300px' }}
          />
        </div>

        <div className="form-group">
          <label className="form-label">CSV File *</label>
          <input
            type="file"
            accept=".csv"
            onChange={handleFileSelect}
            style={{ marginBottom: '8px' }}
          />
          {selectedFile && (
            <p style={{ fontSize: '14px', color: '#666', marginTop: '4px' }}>
              Selected: {selectedFile.name}
            </p>
          )}
          <p style={{ fontSize: '12px', color: '#666', marginTop: '8px' }}>
            Expected columns: Customer Number, Passenger Name, Trip Date, Promised pick-up time,
            Pickup street number, Pickup Street, Pickup City, Promised drop-off time,
            Drop-off street number, Drop-off Street, Drop-off City
          </p>
        </div>

        <button
          className="btn btn-primary"
          onClick={handleImport}
          disabled={loading || !selectedFile}
        >
          {loading ? 'Importing...' : 'Import CSV'}
        </button>

        {success && (
          <div className="alert alert-success" style={{ marginTop: '20px' }}>
            Import completed! {trips.length} trips imported successfully.
            {errors.length > 0 && ` ${errors.length} validation errors found.`}
          </div>
        )}

        {errors.length > 0 && (
          <div style={{ marginTop: '20px' }}>
            <h3 style={{ marginBottom: '12px' }}>Validation Errors ({errors.length})</h3>
            <div style={{ maxHeight: '400px', overflow: 'auto' }}>
              <table className="table">
                <thead>
                  <tr>
                    <th>Row</th>
                    <th>Field</th>
                    <th>Error</th>
                  </tr>
                </thead>
                <tbody>
                  {errors.map((error, idx) => (
                    <tr key={idx}>
                      <td>{error.row_number}</td>
                      <td>{error.field}</td>
                      <td>{error.error_description}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {trips.length > 0 && (
          <div style={{ marginTop: '20px' }}>
            <h3 style={{ marginBottom: '12px' }}>Imported Trips ({trips.length})</h3>
            <div style={{ maxHeight: '400px', overflow: 'auto' }}>
              <table className="table">
                <thead>
                  <tr>
                    <th>Customer #</th>
                    <th>Passenger</th>
                    <th>Pickup Address</th>
                    <th>Dropoff Address</th>
                    <th>Pickup Time</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {trips.slice(0, 20).map(trip => (
                    <tr key={trip.trip_id}>
                      <td>{trip.customer_number}</td>
                      <td>{trip.passenger_name}</td>
                      <td>
                        {trip.pickup_address.street_number} {trip.pickup_address.street}, {trip.pickup_address.city}
                      </td>
                      <td>
                        {trip.dropoff_address.street_number} {trip.dropoff_address.street}, {trip.dropoff_address.city}
                      </td>
                      <td>
                        {trip.promised_pickup_time
                          ? format(new Date(trip.promised_pickup_time), 'MMM dd, yyyy HH:mm')
                          : '-'}
                      </td>
                      <td>
                        <span className={`badge badge-${trip.status === 'ready_for_scheduling' ? 'success' : 'info'}`}>
                          {trip.status}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
              {trips.length > 20 && (
                <p style={{ textAlign: 'center', padding: '12px', color: '#666' }}>
                  Showing first 20 of {trips.length} trips
                </p>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ImportPage;

