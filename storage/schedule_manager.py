"""
Schedule storage and management
"""
import json
from typing import List, Optional
from pathlib import Path
from datetime import datetime

from shared.types.models import Schedule, Route, RouteStop, ClientTrip, TripType, Address
from storage.trip_storage import TripStorage


class ScheduleManager:
    """Manages schedule storage"""
    
    def __init__(self, storage_path: str = "data/schedules"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.trip_storage = TripStorage()
    
    def save_schedule(self, schedule: Schedule):
        """Save schedule to file"""
        file_path = self.storage_path / f"{schedule.schedule_id}.json"
        
        data = {
            'schedule_id': schedule.schedule_id,
            'service_date': schedule.service_date.isoformat(),
            'created_at': schedule.created_at.isoformat(),
            'updated_at': schedule.updated_at.isoformat(),
            'routes': [self._route_to_dict(route) for route in schedule.routes],
            'unassigned_trips': [self._trip_to_dict(trip) for trip in schedule.unassigned_trips]
        }
        
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2, default=str)
    
    def get_schedule(self, schedule_id: str) -> Optional[Schedule]:
        """Load schedule from file"""
        file_path = self.storage_path / f"{schedule_id}.json"
        if not file_path.exists():
            return None
        
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        return self._dict_to_schedule(data)
    
    def _route_to_dict(self, route: Route) -> dict:
        """Convert Route to dictionary"""
        return {
            'route_id': route.route_id,
            'driver_id': route.driver_id,
            'service_date': route.service_date.isoformat(),
            'start_location': {
                'street_number': route.start_location.street_number,
                'street': route.start_location.street,
                'city': route.start_location.city,
                'full_address': str(route.start_location)
            },
            'end_location': {
                'street_number': route.end_location.street_number,
                'street': route.end_location.street,
                'city': route.end_location.city,
                'full_address': str(route.end_location)
            },
            'start_time': route.start_time.isoformat(),
            'end_time': route.end_time.isoformat(),
            'stops': [self._stop_to_dict(stop) for stop in route.stops],
            'total_clients': route.total_clients,
            'total_stops': route.total_stops,
            'total_drive_time_minutes': route.total_drive_time_minutes,
            'total_drive_distance_miles': route.total_drive_distance_miles
        }
    
    def _stop_to_dict(self, stop: RouteStop) -> dict:
        """Convert RouteStop to dictionary"""
        return {
            'stop_number': stop.stop_number,
            'trip_id': stop.client_trip.trip_id,
            'action': stop.action.value,
            'address': {
                'street_number': stop.address.street_number,
                'street': stop.address.street,
                'city': stop.address.city
            },
            'planned_arrival_time': stop.planned_arrival_time.isoformat(),
            'planned_departure_time': stop.planned_departure_time.isoformat(),
            'appointment_time': stop.appointment_time.isoformat() if stop.appointment_time else None,
            'notes': stop.notes
        }
    
    def _trip_to_dict(self, trip: ClientTrip) -> dict:
        """Convert ClientTrip to dictionary"""
        return {
            'trip_id': trip.trip_id,
            'customer_number': trip.customer_number,
            'passenger_name': trip.passenger_name
        }
    
    def _dict_to_schedule(self, data: dict) -> Schedule:
        """Convert dictionary to Schedule"""
        from storage.driver_manager import DriverManager
        
        driver_manager = DriverManager()
        
        routes = []
        for route_data in data.get('routes', []):
            driver = driver_manager.get_driver(route_data['driver_id'])
            if not driver:
                continue
            
            stops = []
            for stop_data in route_data.get('stops', []):
                # Get trip from storage
                trip = self.trip_storage.get_trips_by_ids(
                    data['service_date'],
                    [stop_data['trip_id']]
                )
                if not trip:
                    continue
                trip = trip[0]
                
                address = Address(
                    street_number=stop_data['address']['street_number'],
                    street=stop_data['address']['street'],
                    city=stop_data['address']['city']
                )
                
                stop = RouteStop(
                    stop_number=stop_data['stop_number'],
                    client_trip=trip,
                    action=TripType(stop_data['action']),
                    address=address,
                    planned_arrival_time=datetime.fromisoformat(stop_data['planned_arrival_time']),
                    planned_departure_time=datetime.fromisoformat(stop_data['planned_departure_time']),
                    appointment_time=datetime.fromisoformat(stop_data['appointment_time']) if stop_data.get('appointment_time') else None,
                    notes=stop_data.get('notes')
                )
                stops.append(stop)
            
            start_addr = Address(
                street_number=route_data['start_location']['street_number'],
                street=route_data['start_location']['street'],
                city=route_data['start_location']['city']
            )
            
            end_addr = Address(
                street_number=route_data['end_location']['street_number'],
                street=route_data['end_location']['street'],
                city=route_data['end_location']['city']
            )
            
            route = Route(
                route_id=route_data['route_id'],
                driver_id=route_data['driver_id'],
                service_date=datetime.fromisoformat(route_data['service_date']),
                start_location=start_addr,
                end_location=end_addr,
                start_time=datetime.fromisoformat(route_data['start_time']),
                end_time=datetime.fromisoformat(route_data['end_time']),
                stops=stops,
                total_clients=route_data.get('total_clients', 0),
                total_stops=route_data.get('total_stops', 0),
                total_drive_time_minutes=route_data.get('total_drive_time_minutes', 0),
                total_drive_distance_miles=route_data.get('total_drive_distance_miles', 0)
            )
            routes.append(route)
        
        unassigned = []
        for trip_data in data.get('unassigned_trips', []):
            trips = self.trip_storage.get_trips_by_ids(
                data['service_date'],
                [trip_data['trip_id']]
            )
            if trips:
                unassigned.append(trips[0])
        
        schedule = Schedule(
            schedule_id=data['schedule_id'],
            service_date=datetime.fromisoformat(data['service_date']),
            created_at=datetime.fromisoformat(data['created_at']),
            updated_at=datetime.fromisoformat(data['updated_at']),
            routes=routes,
            unassigned_trips=unassigned
        )
        
        return schedule
    
    def export_to_csv(self, schedule: Schedule, output_path: str):
        """Export schedule to CSV"""
        import pandas as pd
        
        rows = []
        for route in schedule.routes:
            for stop in route.stops:
                rows.append({
                    'Driver ID': route.driver_id,
                    'Stop #': stop.stop_number,
                    'Action': stop.action.value,
                    'Customer #': stop.client_trip.customer_number,
                    'Passenger Name': stop.client_trip.passenger_name,
                    'Address': f"{stop.address.street_number} {stop.address.street}, {stop.address.city}",
                    'Arrival Time': stop.planned_arrival_time.strftime('%Y-%m-%d %H:%M'),
                    'Departure Time': stop.planned_departure_time.strftime('%Y-%m-%d %H:%M'),
                    'Appointment Time': stop.appointment_time.strftime('%Y-%m-%d %H:%M') if stop.appointment_time else '',
                    'Notes': stop.notes or ''
                })
        
        df = pd.DataFrame(rows)
        df.to_csv(output_path, index=False)
