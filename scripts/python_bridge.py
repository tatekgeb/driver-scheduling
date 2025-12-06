#!/usr/bin/env python3
"""
Python bridge for Electron IPC communication
Handles all API calls from the desktop application
"""
import sys
import json
from pathlib import Path
from datetime import datetime, time as dt_time

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from main import SchedulingSystem
from shared.types.models import Driver, Address, TripStatus
from storage.trip_storage import TripStorage


def serialize_driver(driver: Driver) -> dict:
    """Convert Driver object to dictionary"""
    return {
        'driver_id': driver.driver_id,
        'name': driver.name,
        'home_address': {
            'street_number': driver.home_address.street_number,
            'street': driver.home_address.street,
            'city': driver.home_address.city,
            'state': driver.home_address.state,
            'zip_code': driver.home_address.zip_code,
            'full_address': str(driver.home_address),
            'latitude': driver.home_address.latitude,
            'longitude': driver.home_address.longitude
        },
        'phone': driver.phone,
        'vehicle_type': driver.vehicle_type,
        'capacity': driver.capacity,
        'active': driver.active,
        'service_days': driver.service_days,
        'daily_start_time': driver.daily_start_time.isoformat() if driver.daily_start_time else None,
        'daily_end_time': driver.daily_end_time.isoformat() if driver.daily_end_time else None,
        'max_daily_distance': driver.max_daily_distance,
        'max_daily_duration': driver.max_daily_duration
    }


def serialize_trip(trip) -> dict:
    """Convert ClientTrip object to dictionary"""
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
        'status': trip.status.value
    }


def serialize_route(route) -> dict:
    """Convert Route object to dictionary"""
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
        'stops': [{
            'stop_number': stop.stop_number,
            'client_trip': serialize_trip(stop.client_trip),
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
        } for stop in route.stops],
        'total_clients': route.total_clients,
        'total_stops': route.total_stops,
        'total_drive_time_minutes': route.total_drive_time_minutes,
        'total_drive_distance_miles': route.total_drive_distance_miles
    }


def serialize_schedule(schedule) -> dict:
    """Convert Schedule object to dictionary"""
    return {
        'schedule_id': schedule.schedule_id,
        'service_date': schedule.service_date.isoformat(),
        'created_at': schedule.created_at.isoformat(),
        'updated_at': schedule.updated_at.isoformat(),
        'routes': [serialize_route(route) for route in schedule.routes],
        'unassigned_trips': [serialize_trip(trip) for trip in schedule.unassigned_trips]
    }


def deserialize_driver(data: dict) -> Driver:
    """Convert dictionary to Driver object"""
    addr = data['home_address']
    address = Address(
        street_number=addr.get('street_number', ''),
        street=addr.get('street', ''),
        city=addr.get('city', ''),
        state=addr.get('state'),
        zip_code=addr.get('zip_code'),
        full_address=addr.get('full_address'),
        latitude=addr.get('latitude'),
        longitude=addr.get('longitude')
    )
    
    start_time = None
    if data.get('daily_start_time'):
        try:
            parts = data['daily_start_time'].split(':')
            start_time = dt_time(int(parts[0]), int(parts[1]))
        except:
            pass
    
    end_time = None
    if data.get('daily_end_time'):
        try:
            parts = data['daily_end_time'].split(':')
            end_time = dt_time(int(parts[0]), int(parts[1]))
        except:
            pass
    
    return Driver(
        driver_id=data['driver_id'],
        name=data['name'],
        home_address=address,
        phone=data.get('phone'),
        vehicle_type=data.get('vehicle_type'),
        capacity=data.get('capacity'),
        active=data.get('active', True),  # Default to active if not specified
        service_days=data.get('service_days', []),
        daily_start_time=start_time,
        daily_end_time=end_time,
        max_daily_distance=data.get('max_daily_distance'),
        max_daily_duration=data.get('max_daily_duration')
    )


def main():
    if len(sys.argv) < 2:
        print(json.dumps({'error': 'No method specified'}), file=sys.stderr)
        sys.exit(1)
    
    method = sys.argv[1]
    args = json.loads(sys.argv[2]) if len(sys.argv) > 2 else []
    
    try:
        system = SchedulingSystem()
        trip_storage = TripStorage()
        
        if method == 'getDrivers':
            drivers = system.driver_manager.get_all_drivers()
            result = [serialize_driver(d) for d in drivers]
            print(json.dumps(result))
        
        elif method == 'createDriver':
            driver_data = args[0]
            driver = deserialize_driver(driver_data)
            created = system.driver_manager.create_driver(driver)
            print(json.dumps(serialize_driver(created)))
        
        elif method == 'updateDriver':
            driver_id = args[0]
            driver_data = args[1]
            driver = deserialize_driver(driver_data)
            updated = system.driver_manager.update_driver(driver_id, driver)
            print(json.dumps(serialize_driver(updated)))
        
        elif method == 'deleteDriver':
            driver_id = args[0]
            result = system.driver_manager.delete_driver(driver_id)
            print(json.dumps({'success': result}))
        
        elif method == 'importCSV':
            file_path = args[0]
            service_date_str = args[1]
            
            trips, errors = system.import_client_csv(file_path, service_date_str)
            
            # Store trips for later use
            trip_storage.save_trips(service_date_str, trips)
            
            result = {
                'trips': [serialize_trip(t) for t in trips],
                'errors': [{
                    'row_number': e.row_number,
                    'field': e.field,
                    'error_description': e.error_description
                } for e in errors]
            }
            print(json.dumps(result))
        
        elif method == 'generateSchedule':
            service_date_str = args[0]
            trip_ids = args[1] if len(args) > 1 else []
            locked_assignments = args[2] if len(args) > 2 else {}
            
            service_date = datetime.fromisoformat(service_date_str)
            
            # Get trips from storage
            if trip_ids:
                trips = trip_storage.get_trips_by_ids(service_date_str, trip_ids)
            else:
                trips = trip_storage.get_trips_for_date(service_date_str)
            
            if not trips:
                print(json.dumps({'error': 'No trips found for this service date. Please import client data first.'}), file=sys.stderr)
                sys.exit(1)
            
            schedule = system.generate_schedule(service_date, trips, locked_assignments)
            
            # Save schedule
            from storage.schedule_manager import ScheduleManager
            schedule_manager = ScheduleManager()
            schedule_manager.save_schedule(schedule)
            
            print(json.dumps(serialize_schedule(schedule)))
        
        elif method == 'getSchedule':
            schedule_id = args[0]
            from storage.schedule_manager import ScheduleManager
            schedule_manager = ScheduleManager()
            schedule = schedule_manager.get_schedule(schedule_id)
            if schedule:
                print(json.dumps(serialize_schedule(schedule)))
            else:
                print(json.dumps({'error': 'Schedule not found'}), file=sys.stderr)
                sys.exit(1)
        
        elif method == 'reassignTrip':
            trip_id = args[0]
            driver_id = args[1]
            # TODO: Implement trip reassignment
            print(json.dumps({'error': 'Not yet implemented'}), file=sys.stderr)
            sys.exit(1)
        
        elif method == 'exportScheduleToCSV':
            schedule_id = args[0]
            output_path = args[1]
            from storage.schedule_manager import ScheduleManager
            schedule_manager = ScheduleManager()
            schedule = schedule_manager.get_schedule(schedule_id)
            if schedule:
                schedule_manager.export_to_csv(schedule, output_path)
                print(json.dumps({'success': True}))
            else:
                print(json.dumps({'error': 'Schedule not found'}), file=sys.stderr)
                sys.exit(1)
        
        else:
            print(json.dumps({'error': f'Unknown method: {method}'}), file=sys.stderr)
            sys.exit(1)
    
    except Exception as e:
        import traceback
        error_msg = f'{str(e)}\n{traceback.format_exc()}'
        print(json.dumps({'error': error_msg}), file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
