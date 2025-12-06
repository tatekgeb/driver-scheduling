import React, { useState, useEffect } from 'react';
import { Driver } from '../services/api';

interface DriverFormProps {
  driver?: Driver | null;
  onSubmit: (driver: Driver) => void;
  onCancel: () => void;
}

const DriverForm: React.FC<DriverFormProps> = ({ driver, onSubmit, onCancel }) => {
  const [formData, setFormData] = useState<Partial<Driver>>({
    driver_id: '',
    name: '',
    home_address: {
      street_number: '',
      street: '',
      city: '',
    },
    phone: '',
    vehicle_type: '',
    capacity: undefined,
    active: true,
    service_days: [],
    daily_start_time: '',
    daily_end_time: '',
    max_daily_distance: undefined,
    max_daily_duration: undefined,
  });

  useEffect(() => {
    if (driver) {
      setFormData({
        ...driver,
        daily_start_time: driver.daily_start_time || '',
        daily_end_time: driver.daily_end_time || '',
      });
    }
  }, [driver]);

  const handleChange = (field: string, value: any) => {
    if (field.startsWith('home_address.')) {
      const addressField = field.split('.')[1];
      setFormData(prev => ({
        ...prev,
        home_address: {
          ...prev.home_address!,
          [addressField]: value,
        },
      }));
    } else {
      setFormData(prev => ({ ...prev, [field]: value }));
    }
  };

  const handleServiceDayToggle = (day: string) => {
    setFormData(prev => {
      const days = prev.service_days || [];
      const newDays = days.includes(day)
        ? days.filter(d => d !== day)
        : [...days, day];
      return { ...prev, service_days: newDays };
    });
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    const driverData: Driver = {
      driver_id: formData.driver_id || `DRIVER_${Date.now()}`,
      name: formData.name || '',
      home_address: formData.home_address!,
      phone: formData.phone || undefined,
      vehicle_type: formData.vehicle_type || undefined,
      capacity: formData.capacity,
      active: formData.active !== undefined ? formData.active : true,
      service_days: formData.service_days || [],
      daily_start_time: formData.daily_start_time || undefined,
      daily_end_time: formData.daily_end_time || undefined,
      max_daily_distance: formData.max_daily_distance,
      max_daily_duration: formData.max_daily_duration,
    };

    onSubmit(driverData);
  };

  const daysOfWeek = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];

  return (
    <form onSubmit={handleSubmit} style={{ marginTop: '20px', padding: '20px', background: '#f8f9fa', borderRadius: '8px' }}>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
        <div className="form-group">
          <label className="form-label">Driver ID *</label>
          <input
            type="text"
            className="form-input"
            value={formData.driver_id}
            onChange={(e) => handleChange('driver_id', e.target.value)}
            required
            disabled={!!driver}
          />
        </div>

        <div className="form-group">
          <label className="form-label">Name *</label>
          <input
            type="text"
            className="form-input"
            value={formData.name}
            onChange={(e) => handleChange('name', e.target.value)}
            required
          />
        </div>

        <div className="form-group">
          <label className="form-label">Street Number *</label>
          <input
            type="text"
            className="form-input"
            value={formData.home_address?.street_number || ''}
            onChange={(e) => handleChange('home_address.street_number', e.target.value)}
            required
          />
        </div>

        <div className="form-group">
          <label className="form-label">Street *</label>
          <input
            type="text"
            className="form-input"
            value={formData.home_address?.street || ''}
            onChange={(e) => handleChange('home_address.street', e.target.value)}
            required
          />
        </div>

        <div className="form-group">
          <label className="form-label">City *</label>
          <input
            type="text"
            className="form-input"
            value={formData.home_address?.city || ''}
            onChange={(e) => handleChange('home_address.city', e.target.value)}
            required
          />
        </div>

        <div className="form-group">
          <label className="form-label">Phone</label>
          <input
            type="text"
            className="form-input"
            value={formData.phone || ''}
            onChange={(e) => handleChange('phone', e.target.value)}
          />
        </div>

        <div className="form-group">
          <label className="form-label">Vehicle Type</label>
          <input
            type="text"
            className="form-input"
            value={formData.vehicle_type || ''}
            onChange={(e) => handleChange('vehicle_type', e.target.value)}
          />
        </div>

        <div className="form-group">
          <label className="form-label">Capacity</label>
          <input
            type="number"
            className="form-input"
            value={formData.capacity || ''}
            onChange={(e) => handleChange('capacity', e.target.value ? parseInt(e.target.value) : undefined)}
          />
        </div>

        <div className="form-group">
          <label className="form-label">Status</label>
          <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
            <label style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <input
                type="radio"
                name="active"
                checked={formData.active === true}
                onChange={() => handleChange('active', true)}
              />
              <span>Active</span>
            </label>
            <label style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <input
                type="radio"
                name="active"
                checked={formData.active === false}
                onChange={() => handleChange('active', false)}
              />
              <span>Inactive</span>
            </label>
          </div>
          <p style={{ fontSize: '12px', color: '#666', marginTop: '4px' }}>
            Only active drivers will be used when generating schedules.
          </p>
        </div>

        <div className="form-group">
          <label className="form-label">Daily Start Time</label>
          <input
            type="time"
            className="form-input"
            value={formData.daily_start_time || ''}
            onChange={(e) => handleChange('daily_start_time', e.target.value)}
          />
        </div>

        <div className="form-group">
          <label className="form-label">Daily End Time</label>
          <input
            type="time"
            className="form-input"
            value={formData.daily_end_time || ''}
            onChange={(e) => handleChange('daily_end_time', e.target.value)}
          />
        </div>
      </div>

      <div className="form-group">
        <label className="form-label">Service Days</label>
        <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
          {daysOfWeek.map(day => (
            <label key={day} style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <input
                type="checkbox"
                checked={formData.service_days?.includes(day) || false}
                onChange={() => handleServiceDayToggle(day)}
              />
              <span>{day}</span>
            </label>
          ))}
        </div>
      </div>

      <div style={{ display: 'flex', gap: '12px', justifyContent: 'flex-end', marginTop: '20px' }}>
        <button type="button" className="btn btn-secondary" onClick={onCancel}>
          Cancel
        </button>
        <button type="submit" className="btn btn-primary">
          {driver ? 'Update' : 'Create'} Driver
        </button>
      </div>
    </form>
  );
};

export default DriverForm;

