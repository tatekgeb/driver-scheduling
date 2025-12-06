/**
 * API service for communicating with Flask backend
 * Uses HTTP requests instead of Electron IPC
 */

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

// Helper function for API calls
async function apiCall(endpoint: string, options: RequestInit = {}): Promise<any> {
  const url = `${API_BASE_URL}${endpoint}`;
  const response = await fetch(url, {
    ...options,
    credentials: 'include', // Include cookies for session
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ error: 'Request failed' }));
    throw new Error(error.error || `HTTP ${response.status}`);
  }

  return response.json();
}

// Helper for file uploads
async function apiUpload(endpoint: string, formData: FormData): Promise<any> {
  const url = `${API_BASE_URL}${endpoint}`;
  const response = await fetch(url, {
    method: 'POST',
    body: formData,
    credentials: 'include',
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ error: 'Upload failed' }));
    throw new Error(error.error || `HTTP ${response.status}`);
  }

  return response.json();
}

export interface Driver {
  driver_id: string;
  name: string;
  home_address: {
    street_number: string;
    street: string;
    city: string;
    state?: string;
    zip_code?: string;
    full_address?: string;
    latitude?: number;
    longitude?: number;
  };
  phone?: string;
  vehicle_type?: string;
  capacity?: number;
  active: boolean;
  service_days: string[];
  daily_start_time?: string;
  daily_end_time?: string;
  max_daily_distance?: number;
  max_daily_duration?: number;
}

export interface ClientTrip {
  trip_id: string;
  customer_number: string;
  passenger_name: string;
  trip_date: string;
  trip_type: 'pickup' | 'dropoff';
  pickup_address: {
    street_number: string;
    street: string;
    city: string;
    latitude?: number;
    longitude?: number;
  };
  dropoff_address: {
    street_number: string;
    street: string;
    city: string;
    latitude?: number;
    longitude?: number;
  };
  promised_pickup_time?: string;
  promised_dropoff_time?: string;
  appointment_time?: string;
  arrival_buffer_minutes: number;
  mobility_needs?: string;
  special_notes?: string;
  status: string;
}

export interface RouteStop {
  stop_number: number;
  client_trip: ClientTrip;
  action: 'pickup' | 'dropoff';
  address: {
    street_number: string;
    street: string;
    city: string;
  };
  planned_arrival_time: string;
  planned_departure_time: string;
  appointment_time?: string;
  notes?: string;
}

export interface Route {
  route_id: string;
  driver_id: string;
  service_date: string;
  start_location: any;
  end_location: any;
  start_time: string;
  end_time: string;
  stops: RouteStop[];
  total_clients: number;
  total_stops: number;
  total_drive_time_minutes: number;
  total_drive_distance_miles: number;
}

export interface Schedule {
  schedule_id: string;
  service_date: string;
  created_at: string;
  updated_at: string;
  routes: Route[];
  unassigned_trips: ClientTrip[];
}

export interface ValidationError {
  row_number: number;
  field: string;
  error_description: string;
}

class APIService {
  // Authentication
  async login(username: string, password: string): Promise<{ user_id: string; role: string; driver_id?: string }> {
    return apiCall('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ username, password }),
    });
  }

  async logout(): Promise<void> {
    return apiCall('/auth/logout', { method: 'POST' });
  }

  async getCurrentUser(): Promise<{ user_id: string; role: string; driver_id?: string }> {
    return apiCall('/auth/me');
  }

  // Driver operations
  async getDrivers(): Promise<Driver[]> {
    return apiCall('/drivers');
  }

  async createDriver(driver: Driver): Promise<Driver> {
    return apiCall('/drivers', {
      method: 'POST',
      body: JSON.stringify(driver),
    });
  }

  async updateDriver(driverId: string, driver: Driver): Promise<Driver> {
    return apiCall(`/drivers/${driverId}`, {
      method: 'PUT',
      body: JSON.stringify(driver),
    });
  }

  async deleteDriver(driverId: string): Promise<boolean> {
    await apiCall(`/drivers/${driverId}`, { method: 'DELETE' });
    return true;
  }

  // CSV Import
  async importCSV(file: File, serviceDate: string): Promise<{
    trips: ClientTrip[];
    errors: ValidationError[];
  }> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('service_date', serviceDate);
    return apiUpload('/import/csv', formData);
  }

  // Schedule operations
  async generateSchedule(
    serviceDate: string,
    tripIds: string[] = [],
    lockedAssignments?: Record<string, string>
  ): Promise<Schedule> {
    return apiCall('/schedules/generate', {
      method: 'POST',
      body: JSON.stringify({
        service_date: serviceDate,
        trip_ids: tripIds,
        locked_assignments: lockedAssignments || {},
      }),
    });
  }

  async getSchedule(scheduleId: string): Promise<Schedule> {
    return apiCall(`/schedules/${scheduleId}`);
  }

  async getDriverSchedule(scheduleId: string, driverId: string): Promise<{
    schedule_id: string;
    service_date: string;
    route: Route;
  }> {
    return apiCall(`/schedules/${scheduleId}/driver/${driverId}`);
  }

  async listSchedules(serviceDate: string): Promise<Schedule[]> {
    return apiCall(`/schedules?service_date=${serviceDate}`);
  }

  async reassignTrip(tripId: string, driverId: string): Promise<Schedule> {
    // TODO: Implement in backend
    throw new Error('Not yet implemented');
  }

  // Export
  async exportScheduleToCSV(scheduleId: string): Promise<Blob> {
    const url = `${API_BASE_URL}/schedules/${scheduleId}/export`;
    const response = await fetch(url, {
      credentials: 'include',
    });
    if (!response.ok) {
      throw new Error('Export failed');
    }
    return response.blob();
  }
}

export const api = new APIService();

