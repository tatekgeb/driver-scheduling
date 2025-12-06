"""
Mapping API service for geocoding and distance/time calculations
"""
import json
import hashlib
from typing import Optional, Tuple
from pathlib import Path
from datetime import datetime
import time

from shared.types.models import Address, TravelInfo
from config.config import MappingAPIConfig


class MappingService:
    """Service for geocoding and route calculations"""
    
    def __init__(self, config: MappingAPIConfig):
        self.config = config
        self.cache_dir = Path("cache/geocoding")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.api_client = self._create_api_client()
    
    def _create_api_client(self):
        """Create API client based on provider"""
        if self.config.provider == "google":
            return GoogleMapsClient(self.config.api_key)
        elif self.config.provider == "mapbox":
            # Future: MapboxClient
            raise NotImplementedError("Mapbox provider not yet implemented")
        else:
            raise ValueError(f"Unknown mapping provider: {self.config.provider}")
    
    def _get_cache_key(self, address: str) -> str:
        """Generate cache key for address"""
        return hashlib.md5(address.encode()).hexdigest()
    
    def _get_cached_geocode(self, address: str) -> Optional[Tuple[float, float]]:
        """Get cached geocoding result"""
        if not self.config.cache_geocoding:
            return None
        
        cache_key = self._get_cache_key(address)
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    data = json.load(f)
                    # Check if cache is still valid
                    cached_at = datetime.fromisoformat(data['cached_at'])
                    age_days = (datetime.now() - cached_at).days
                    if age_days < self.config.cache_duration_days:
                        return (data['latitude'], data['longitude'])
            except:
                pass
        
        return None
    
    def _cache_geocode(self, address: str, lat: float, lon: float):
        """Cache geocoding result"""
        if not self.config.cache_geocoding:
            return
        
        cache_key = self._get_cache_key(address)
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        data = {
            'address': address,
            'latitude': lat,
            'longitude': lon,
            'cached_at': datetime.now().isoformat()
        }
        
        with open(cache_file, 'w') as f:
            json.dump(data, f)
    
    def geocode_address(self, address: Address) -> Address:
        """
        Geocode an address to get latitude/longitude
        
        Args:
            address: Address object to geocode
        
        Returns:
            Address object with latitude/longitude populated
        """
        # If already geocoded, return as-is
        if address.latitude is not None and address.longitude is not None:
            return address
        
        # Build address string
        address_str = str(address)
        
        # Check cache
        cached = self._get_cached_geocode(address_str)
        if cached:
            address.latitude, address.longitude = cached
            return address
        
        # Geocode via API
        try:
            lat, lon = self.api_client.geocode(address_str)
            address.latitude = lat
            address.longitude = lon
            
            # Cache result
            self._cache_geocode(address_str, lat, lon)
            
            return address
        except Exception as e:
            raise Exception(f"Geocoding failed for address '{address_str}': {str(e)}")
    
    def calculate_travel_info(
        self,
        from_address: Address,
        to_address: Address,
        departure_time: Optional[datetime] = None
    ) -> TravelInfo:
        """
        Calculate travel distance and time between two addresses
        
        Args:
            from_address: Starting address
            to_address: Destination address
            departure_time: Optional departure time for traffic-aware calculations
        
        Returns:
            TravelInfo object with distance and duration
        """
        # Ensure addresses are geocoded
        from_address = self.geocode_address(from_address)
        to_address = self.geocode_address(to_address)
        
        # Calculate route
        try:
            distance, duration = self.api_client.calculate_route(
                from_address,
                to_address,
                departure_time=departure_time,
                use_traffic=self.config.use_traffic
            )
            
            return TravelInfo(
                from_address=from_address,
                to_address=to_address,
                distance_miles=distance,
                duration_minutes=duration,
                traffic_adjusted=self.config.use_traffic and departure_time is not None,
                calculated_at=datetime.now()
            )
        except Exception as e:
            raise Exception(f"Route calculation failed: {str(e)}")


class GoogleMapsClient:
    """Google Maps API client"""
    
    def __init__(self, api_key: Optional[str]):
        if not api_key:
            raise ValueError("Google Maps API key is required")
        self.api_key = api_key
        self.base_url = "https://maps.googleapis.com/maps/api"
    
    def geocode(self, address: str) -> Tuple[float, float]:
        """
        Geocode an address using Google Maps API
        
        Returns:
            Tuple of (latitude, longitude)
        """
        import requests
        
        url = f"{self.base_url}/geocode/json"
        params = {
            'address': address,
            'key': self.api_key
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        
        if data['status'] != 'OK':
            raise Exception(f"Geocoding failed: {data.get('error_message', data['status'])}")
        
        location = data['results'][0]['geometry']['location']
        return (location['lat'], location['lng'])
    
    def calculate_route(
        self,
        from_address: Address,
        to_address: Address,
        departure_time: Optional[datetime] = None,
        use_traffic: bool = False
    ) -> Tuple[float, float]:
        """
        Calculate route distance and duration
        
        Returns:
            Tuple of (distance_miles, duration_minutes)
        """
        import requests
        
        url = f"{self.base_url}/directions/json"
        
        origin = f"{from_address.latitude},{from_address.longitude}"
        destination = f"{to_address.latitude},{to_address.longitude}"
        
        params = {
            'origin': origin,
            'destination': destination,
            'key': self.api_key,
            'units': 'imperial'  # Get distance in miles
        }
        
        # Add traffic-aware routing if requested
        if use_traffic and departure_time:
            params['departure_time'] = int(departure_time.timestamp())
            params['traffic_model'] = 'best_guess'
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        
        if data['status'] != 'OK':
            raise Exception(f"Route calculation failed: {data.get('error_message', data['status'])}")
        
        route = data['routes'][0]['legs'][0]
        distance_miles = route['distance']['value'] / 1609.34  # Convert meters to miles
        duration_seconds = route['duration']['value']
        
        # If traffic-aware, use duration_in_traffic
        if use_traffic and 'duration_in_traffic' in route:
            duration_seconds = route['duration_in_traffic']['value']
        
        duration_minutes = duration_seconds / 60.0
        
        return (distance_miles, duration_minutes)

