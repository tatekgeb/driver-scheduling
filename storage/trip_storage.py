"""
Trip storage for imported client trips
"""
import json
from typing import List, Optional
from pathlib import Path
from datetime import datetime

from shared.types.models import ClientTrip, TripStatus
from etl.csv_ingestion import ValidationError


class TripStorage:
    """Manages storage of imported client trips"""
    
    def __init__(self, storage_path: str = "data/trips"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
    
    def _get_file_path(self, service_date: str) -> Path:
        """Get file path for a service date"""
        return self.storage_path / f"{service_date}.json"
    
    def save_trips(self, service_date: str, trips: List[ClientTrip]):
        """Save trips for a service date"""
        file_path = self._get_file_path(service_date)
        
        data = {
            'service_date': service_date,
            'trips': [self._trip_to_dict(trip) for trip in trips],
            'saved_at': datetime.now().isoformat()
        }
        
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2, default=str)
    
    def get_trips_for_date(self, service_date: str) -> List[ClientTrip]:
        """Get all trips for a service date"""
        file_path = self._get_file_path(service_date)
        
        if not file_path.exists():
            return []
        
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        return [self._dict_to_trip(t) for t in data.get('trips', [])]
    
    def get_trips_by_ids(self, service_date: str, trip_ids: List[str]) -> List[ClientTrip]:
        """Get specific trips by their IDs"""
        all_trips = self.get_trips_for_date(service_date)
        trip_dict = {t.trip_id: t for t in all_trips}
        return [trip_dict[tid] for tid in trip_ids if tid in trip_dict]
    
    def _trip_to_dict(self, trip: ClientTrip) -> dict:
        """Convert ClientTrip to dictionary"""
        return {
            'trip_id': trip.trip_id,
            'customer_number': trip.customer_number,
            'passenger_name': trip.passenger_name,
            'trip_date': trip.trip_date.isoformat(),
            'trip_type': trip.trip_type.value,
            'pickup_address': {
                'street_number': trip.pickup_address.street_number,
                'street': trip.pickup_address.street,
                'city': trip.pickup_address.city,
                'latitude': trip.pickup_address.latitude,
                'longitude': trip.pickup_address.longitude
            },
            'dropoff_address': {
                'street_number': trip.dropoff_address.street_number,
                'street': trip.dropoff_address.street,
                'city': trip.dropoff_address.city,
                'latitude': trip.dropoff_address.latitude,
                'longitude': trip.dropoff_address.longitude
            },
            'promised_pickup_time': trip.promised_pickup_time.isoformat() if trip.promised_pickup_time else None,
            'promised_dropoff_time': trip.promised_dropoff_time.isoformat() if trip.promised_dropoff_time else None,
            'appointment_time': trip.appointment_time.isoformat() if trip.appointment_time else None,
            'arrival_buffer_minutes': trip.arrival_buffer_minutes,
            'mobility_needs': trip.mobility_needs,
            'special_notes': trip.special_notes,
            'hard_driver_constraints': trip.hard_driver_constraints,
            'status': trip.status.value,
            'assigned_driver_id': trip.assigned_driver_id
        }
    
    def _dict_to_trip(self, data: dict) -> ClientTrip:
        """Convert dictionary to ClientTrip"""
        from shared.types.models import Address, TripType
        
        pickup_addr = data['pickup_address']
        dropoff_addr = data['dropoff_address']
        
        pickup_address = Address(
            street_number=pickup_addr.get('street_number', ''),
            street=pickup_addr.get('street', ''),
            city=pickup_addr.get('city', ''),
            latitude=pickup_addr.get('latitude'),
            longitude=pickup_addr.get('longitude')
        )
        
        dropoff_address = Address(
            street_number=dropoff_addr.get('street_number', ''),
            street=dropoff_addr.get('street', ''),
            city=dropoff_addr.get('city', ''),
            latitude=dropoff_addr.get('latitude'),
            longitude=dropoff_addr.get('longitude')
        )
        
        trip = ClientTrip(
            trip_id=data['trip_id'],
            customer_number=data['customer_number'],
            passenger_name=data['passenger_name'],
            trip_date=datetime.fromisoformat(data['trip_date']),
            trip_type=TripType(data['trip_type']),
            pickup_address=pickup_address,
            dropoff_address=dropoff_address,
            promised_pickup_time=datetime.fromisoformat(data['promised_pickup_time']) if data.get('promised_pickup_time') else None,
            promised_dropoff_time=datetime.fromisoformat(data['promised_dropoff_time']) if data.get('promised_dropoff_time') else None,
            appointment_time=datetime.fromisoformat(data['appointment_time']) if data.get('appointment_time') else None,
            arrival_buffer_minutes=data.get('arrival_buffer_minutes', 5),
            mobility_needs=data.get('mobility_needs'),
            special_notes=data.get('special_notes'),
            hard_driver_constraints=data.get('hard_driver_constraints', []),
            status=TripStatus(data.get('status', 'imported')),
            assigned_driver_id=data.get('assigned_driver_id')
        )
        
        return trip

