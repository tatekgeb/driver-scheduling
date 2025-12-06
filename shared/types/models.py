"""
Data models for the Driver-Client Scheduling System
"""
from dataclasses import dataclass
from datetime import datetime, time
from typing import Optional, List
from enum import Enum


class TripType(Enum):
    """Type of trip"""
    PICKUP = "pickup"  # Home to appointment
    DROPOFF = "dropoff"  # Appointment to home


class TripStatus(Enum):
    """Status of a client trip"""
    IMPORTED = "imported"
    READY_FOR_SCHEDULING = "ready_for_scheduling"
    SCHEDULED = "scheduled"
    INVALID = "invalid"


@dataclass
class Address:
    """Represents a physical address"""
    street_number: str
    street: str
    city: str
    state: Optional[str] = None
    zip_code: Optional[str] = None
    full_address: Optional[str] = None  # Full formatted address
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    
    def __str__(self):
        if self.full_address:
            return self.full_address
        parts = [self.street_number, self.street, self.city]
        if self.state:
            parts.append(self.state)
        if self.zip_code:
            parts.append(self.zip_code)
        return ", ".join(parts)


@dataclass
class TimeWindow:
    """Time window for pickup or appointment"""
    earliest: datetime
    latest: datetime
    
    def contains(self, dt: datetime) -> bool:
        """Check if datetime is within this window"""
        return self.earliest <= dt <= self.latest


@dataclass
class Driver:
    """Driver information"""
    driver_id: str
    name: str
    home_address: Address
    phone: Optional[str] = None
    vehicle_type: Optional[str] = None
    capacity: Optional[int] = None
    active: bool = True  # Active/Inactive status - only active drivers are used in scheduling
    
    # Availability
    service_days: List[str] = None  # e.g., ["Monday", "Tuesday", ...]
    daily_start_time: time = None  # e.g., time(7, 0) for 07:00
    daily_end_time: time = None  # e.g., time(17, 0) for 17:00
    max_daily_distance: Optional[float] = None  # in miles/km
    max_daily_duration: Optional[int] = None  # in minutes
    
    def __post_init__(self):
        if self.service_days is None:
            self.service_days = []


@dataclass
class ClientTrip:
    """A client trip (pickup or dropoff)"""
    trip_id: str
    customer_number: str
    passenger_name: str
    trip_date: datetime
    trip_type: TripType
    
    # Location
    pickup_address: Address
    dropoff_address: Address
    
    # Time constraints
    promised_pickup_time: Optional[datetime] = None
    promised_dropoff_time: Optional[datetime] = None
    appointment_time: Optional[datetime] = None
    arrival_buffer_minutes: int = 5  # Default 5 minutes
    
    # Additional info
    mobility_needs: Optional[str] = None
    special_notes: Optional[str] = None
    hard_driver_constraints: Optional[List[str]] = None  # Driver IDs that must/must not be assigned
    
    # Status
    status: TripStatus = TripStatus.IMPORTED
    assigned_driver_id: Optional[str] = None
    
    def __post_init__(self):
        if self.hard_driver_constraints is None:
            self.hard_driver_constraints = []


@dataclass
class RouteStop:
    """A single stop in a driver's route"""
    stop_number: int
    client_trip: ClientTrip
    action: TripType  # PICKUP or DROPOFF
    address: Address
    planned_arrival_time: datetime
    planned_departure_time: datetime
    appointment_time: Optional[datetime] = None
    notes: Optional[str] = None


@dataclass
class Route:
    """A driver's route for a service day"""
    route_id: str
    driver_id: str
    service_date: datetime
    start_location: Address
    end_location: Address
    start_time: datetime
    end_time: datetime
    stops: List[RouteStop] = None
    
    # Summary metrics
    total_clients: int = 0
    total_stops: int = 0
    total_drive_time_minutes: float = 0.0
    total_drive_distance_miles: float = 0.0
    
    def __post_init__(self):
        if self.stops is None:
            self.stops = []


@dataclass
class Schedule:
    """Complete schedule for a service day"""
    schedule_id: str
    service_date: datetime
    created_at: datetime
    updated_at: datetime
    routes: List[Route] = None
    unassigned_trips: List[ClientTrip] = None
    
    def __post_init__(self):
        if self.routes is None:
            self.routes = []
        if self.unassigned_trips is None:
            self.unassigned_trips = []


@dataclass
class TravelInfo:
    """Travel information between two points"""
    from_address: Address
    to_address: Address
    distance_miles: float
    duration_minutes: float
    traffic_adjusted: bool = False
    calculated_at: Optional[datetime] = None

