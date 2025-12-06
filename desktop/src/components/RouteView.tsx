import React from 'react';
import { Route, RouteStop } from '../services/api';
import { format } from 'date-fns';

interface RouteViewProps {
  route: Route;
}

const RouteView: React.FC<RouteViewProps> = ({ route }) => {
  return (
    <div style={{ marginTop: '20px' }}>
      <table className="table">
        <thead>
          <tr>
            <th>Stop #</th>
            <th>Action</th>
            <th>Client</th>
            <th>Address</th>
            <th>Arrival</th>
            <th>Departure</th>
            <th>Appointment</th>
            <th>Notes</th>
          </tr>
        </thead>
        <tbody>
          {route.stops.map((stop: RouteStop) => (
            <tr key={stop.stop_number}>
              <td>{stop.stop_number}</td>
              <td>
                <span className={`badge badge-${stop.action === 'pickup' ? 'info' : 'success'}`}>
                  {stop.action.toUpperCase()}
                </span>
              </td>
              <td>
                <div>
                  <div style={{ fontWeight: '500' }}>{stop.client_trip.passenger_name}</div>
                  <div style={{ fontSize: '12px', color: '#666' }}>
                    #{stop.client_trip.customer_number}
                  </div>
                </div>
              </td>
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
              <td style={{ fontSize: '12px', color: '#666' }}>
                {stop.notes || stop.client_trip.special_notes || '-'}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default RouteView;

