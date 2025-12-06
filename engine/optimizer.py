"""
Optimization engine for driver-client scheduling (VRPTW solver)
"""
from typing import List, Optional, Dict
from datetime import datetime, timedelta
import uuid

from shared.types.models import (
    Driver, ClientTrip, Route, RouteStop, Schedule,
    TripType, TripStatus
)
from engine.mapping_service import MappingService
from config.config import OptimizationConfig, MappingAPIConfig


class OptimizationError(Exception):
    """Exception for optimization errors"""
    pass


class Optimizer:
    """
    Vehicle Routing Problem with Time Windows (VRPTW) optimizer
    """
    
    def __init__(
        self,
        optimization_config: OptimizationConfig,
        mapping_service: MappingService
    ):
        self.config = optimization_config
        self.mapping_service = mapping_service
    
    def optimize_schedule(
        self,
        service_date: datetime,
        drivers: List[Driver],
        client_trips: List[ClientTrip],
        locked_assignments: Optional[Dict[str, str]] = None
    ) -> Schedule:
        """
        Optimize driver assignments for a service date
        
        Args:
            service_date: Date for which to generate schedule
            drivers: Available drivers
            client_trips: Client trips to assign
            locked_assignments: Dict mapping trip_id to driver_id for locked assignments
        
        Returns:
            Schedule object with optimized routes
        """
        if locked_assignments is None:
            locked_assignments = {}
        
        # Filter trips that are ready for scheduling
        ready_trips = [
            trip for trip in client_trips
            if trip.status == TripStatus.READY_FOR_SCHEDULING
        ]
        
        if not ready_trips:
            raise OptimizationError("No trips ready for scheduling")
        
        # Filter to only active drivers
        active_drivers = [d for d in drivers if d.active]
        
        if not active_drivers:
            raise OptimizationError("No active drivers available for scheduling")
        
        if not drivers:
            raise OptimizationError("No drivers available")
        
        # Geocode all addresses
        print("Geocoding addresses...")
        for trip in ready_trips:
            trip.pickup_address = self.mapping_service.geocode_address(trip.pickup_address)
            trip.dropoff_address = self.mapping_service.geocode_address(trip.dropoff_address)
        
        for driver in active_drivers:
            driver.home_address = self.mapping_service.geocode_address(driver.home_address)
        
        # Build distance/time matrix
        print("Building distance matrix...")
        distance_matrix = self._build_distance_matrix(active_drivers, ready_trips)
        
        # Run optimization algorithm
        print("Running optimization...")
        routes = self._solve_vrptw(
            service_date,
            active_drivers,
            ready_trips,
            distance_matrix,
            locked_assignments
        )
        
        # Identify unassigned trips
        assigned_trip_ids = set()
        for route in routes:
            for stop in route.stops:
                assigned_trip_ids.add(stop.client_trip.trip_id)
        
        unassigned_trips = [
            trip for trip in ready_trips
            if trip.trip_id not in assigned_trip_ids
        ]
        
        # Create schedule
        schedule = Schedule(
            schedule_id=str(uuid.uuid4()),
            service_date=service_date,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            routes=routes,
            unassigned_trips=unassigned_trips
        )
        
        return schedule
    
    def _build_distance_matrix(
        self,
        drivers: List[Driver],
        trips: List[ClientTrip]
    ) -> Dict:
        """
        Build distance and time matrix between all locations
        
        Returns:
            Dictionary with distance/time information
        """
        matrix = {}
        
        # Driver home to trip pickups
        for driver in drivers:
            for trip in trips:
                key = (driver.driver_id, trip.trip_id, 'pickup')
                travel_info = self.mapping_service.calculate_travel_info(
                    driver.home_address,
                    trip.pickup_address
                )
                matrix[key] = {
                    'distance': travel_info.distance_miles,
                    'duration': travel_info.duration_minutes
                }
        
        # Between trip locations (pickup to dropoff, dropoff to next pickup, etc.)
        for trip1 in trips:
            for trip2 in trips:
                if trip1.trip_id != trip2.trip_id:
                    # Dropoff of trip1 to pickup of trip2
                    key = (trip1.trip_id, trip2.trip_id, 'dropoff_to_pickup')
                    travel_info = self.mapping_service.calculate_travel_info(
                        trip1.dropoff_address,
                        trip2.pickup_address
                    )
                    matrix[key] = {
                        'distance': travel_info.distance_miles,
                        'duration': travel_info.duration_minutes
                    }
        
        return matrix
    
    def _solve_vrptw(
        self,
        service_date: datetime,
        drivers: List[Driver],
        trips: List[ClientTrip],
        distance_matrix: Dict,
        locked_assignments: Dict[str, str]
    ) -> List[Route]:
        """
        Solve the Vehicle Routing Problem with Time Windows
        
        This is a simplified greedy algorithm. For production, consider using
        a more sophisticated solver like OR-Tools, Gurobi, or similar.
        """
        routes = []
        assigned_trips = set()
        
        # Handle locked assignments first
        for trip_id, driver_id in locked_assignments.items():
            trip = next((t for t in trips if t.trip_id == trip_id), None)
            driver = next((d for d in drivers if d.driver_id == driver_id), None)
            
            if trip and driver:
                route = self._create_route_for_trip(driver, trip, service_date, distance_matrix)
                if route:
                    routes.append(route)
                    assigned_trips.add(trip_id)
        
        # Greedy assignment for remaining trips
        remaining_trips = [t for t in trips if t.trip_id not in assigned_trips]
        remaining_trips.sort(key=lambda t: t.promised_pickup_time or t.trip_date)
        
        for trip in remaining_trips:
            best_driver = None
            best_cost = float('inf')
            best_route = None
            
            for driver in drivers:
                # Check if driver can handle this trip
                if not self._can_driver_handle_trip(driver, trip, service_date):
                    continue
                
                # Try adding to existing route or create new
                route = self._try_add_trip_to_route(driver, trip, routes, service_date, distance_matrix)
                
                if route:
                    cost = self._calculate_route_cost(route)
                    if cost < best_cost:
                        best_cost = cost
                        best_driver = driver
                        best_route = route
            
            if best_route:
                # Update or add route
                existing_route = next((r for r in routes if r.driver_id == best_driver.driver_id), None)
                if existing_route:
                    routes.remove(existing_route)
                routes.append(best_route)
                assigned_trips.add(trip.trip_id)
        
        return routes
    
    def _can_driver_handle_trip(self, driver: Driver, trip: ClientTrip, service_date: datetime) -> bool:
        """Check if driver can handle a trip based on constraints"""
        # Check service day
        day_name = service_date.strftime('%A')
        if driver.service_days and day_name not in driver.service_days:
            return False
        
        # Check hard constraints
        if trip.hard_driver_constraints:
            # If constraints specify required drivers, check if this driver is in the list
            # This is simplified - can be enhanced
            pass
        
        return True
    
    def _create_route_for_trip(
        self,
        driver: Driver,
        trip: ClientTrip,
        service_date: datetime,
        distance_matrix: Dict
    ) -> Optional[Route]:
        """Create a new route starting with a single trip"""
        # Calculate start time (driver's start time or trip pickup time)
        driver_start = datetime.combine(service_date.date(), driver.daily_start_time)
        pickup_time = trip.promised_pickup_time or driver_start
        
        # Get travel time from driver home to pickup
        key = (driver.driver_id, trip.trip_id, 'pickup')
        travel_info = distance_matrix.get(key, {'duration': 0})
        
        departure_time = pickup_time - timedelta(minutes=int(travel_info['duration']))
        if departure_time < driver_start:
            departure_time = driver_start
        
        # Create pickup stop
        pickup_stop = RouteStop(
            stop_number=1,
            client_trip=trip,
            action=TripType.PICKUP,
            address=trip.pickup_address,
            planned_arrival_time=departure_time + timedelta(minutes=int(travel_info['duration'])),
            planned_departure_time=pickup_time,
            appointment_time=trip.appointment_time,
            notes=trip.special_notes
        )
        
        # Calculate dropoff time
        dropoff_time = trip.promised_dropoff_time or (pickup_time + timedelta(minutes=30))
        
        # Create dropoff stop
        dropoff_stop = RouteStop(
            stop_number=2,
            client_trip=trip,
            action=TripType.DROPOFF,
            address=trip.dropoff_address,
            planned_arrival_time=dropoff_time,
            planned_departure_time=dropoff_time,
            appointment_time=trip.appointment_time,
            notes=trip.special_notes
        )
        
        route = Route(
            route_id=str(uuid.uuid4()),
            driver_id=driver.driver_id,
            service_date=service_date,
            start_location=driver.home_address,
            end_location=driver.home_address,  # Return to home
            start_time=departure_time,
            end_time=dropoff_time,
            stops=[pickup_stop, dropoff_stop],
            total_clients=1,
            total_stops=2
        )
        
        return route
    
    def _try_add_trip_to_route(
        self,
        driver: Driver,
        trip: ClientTrip,
        existing_routes: List[Route],
        service_date: datetime,
        distance_matrix: Dict
    ) -> Optional[Route]:
        """Try to add a trip to an existing route or create a new one"""
        # Find existing route for this driver
        existing_route = next((r for r in existing_routes if r.driver_id == driver.driver_id), None)
        
        if existing_route:
            # Try to insert into existing route
            # Simplified: just append for now
            # In production, would need proper insertion logic
            return None  # For now, create new route
        
        # Create new route
        return self._create_route_for_trip(driver, trip, service_date, distance_matrix)
    
    def _calculate_route_cost(self, route: Route) -> float:
        """Calculate cost of a route for optimization"""
        cost = 0.0
        
        # Travel time cost
        cost += route.total_drive_time_minutes * self.config.weight_travel_time
        
        # Distance cost
        cost += route.total_drive_distance_miles * self.config.weight_travel_distance
        
        return cost

