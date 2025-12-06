"""
Configuration management for the Driver Scheduling System
"""
import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class MappingAPIConfig:
    """Configuration for mapping API (Google Maps, etc.)"""
    provider: str = "google"  # "google", "mapbox", etc.
    api_key: Optional[str] = None
    use_traffic: bool = True
    traffic_time_granularity_minutes: int = 15
    cache_geocoding: bool = True
    cache_duration_days: int = 30


@dataclass
class OptimizationConfig:
    """Configuration for optimization engine"""
    # Objective weights
    weight_travel_time: float = 1.0
    weight_travel_distance: float = 0.5
    weight_load_balancing: float = 0.3
    weight_geographic_proximity: float = 0.2
    
    # Constraints
    default_arrival_buffer_minutes: int = 5
    max_route_duration_minutes: Optional[int] = None
    max_clients_per_driver: Optional[int] = None
    
    # Solver settings
    solver_timeout_seconds: int = 300  # 5 minutes
    enable_partial_reoptimization: bool = True


@dataclass
class SystemConfig:
    """System-wide configuration"""
    # Data retention
    raw_file_retention_days: int = 3
    
    # Performance
    max_drivers: int = 50
    max_clients_per_day: int = 500
    scheduling_timeout_minutes: int = 10
    
    # Security
    encrypt_data_at_rest: bool = True
    require_authentication: bool = True
    
    # Paths
    data_directory: str = "data"
    drivers_file: str = "drivers.json"
    schedules_directory: str = "schedules"
    cache_directory: str = "cache"


class Config:
    """Main configuration class"""
    def __init__(self):
        self.mapping_api = MappingAPIConfig(
            api_key=os.getenv("MAPS_API_KEY")
        )
        self.optimization = OptimizationConfig()
        self.system = SystemConfig()
    
    @classmethod
    def from_file(cls, config_path: str) -> 'Config':
        """Load configuration from JSON file"""
        import json
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # Remove BOM if present
                if content.startswith('\ufeff'):
                    content = content[1:]
                data = json.loads(content)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in config file {config_path} at line {e.lineno}, column {e.colno}: {e.msg}")
        except Exception as e:
            raise ValueError(f"Error reading config file {config_path}: {str(e)}")
        
        config = cls()
        if 'mapping_api' in data:
            config.mapping_api = MappingAPIConfig(**data['mapping_api'])
        if 'optimization' in data:
            config.optimization = OptimizationConfig(**data['optimization'])
        if 'system' in data:
            config.system = SystemConfig(**data['system'])
        
        return config
    
    def to_dict(self) -> dict:
        """Convert configuration to dictionary"""
        return {
            'mapping_api': {
                'provider': self.mapping_api.provider,
                'use_traffic': self.mapping_api.use_traffic,
                'traffic_time_granularity_minutes': self.mapping_api.traffic_time_granularity_minutes,
                'cache_geocoding': self.mapping_api.cache_geocoding,
                'cache_duration_days': self.mapping_api.cache_duration_days
            },
            'optimization': {
                'weight_travel_time': self.optimization.weight_travel_time,
                'weight_travel_distance': self.optimization.weight_travel_distance,
                'weight_load_balancing': self.optimization.weight_load_balancing,
                'weight_geographic_proximity': self.optimization.weight_geographic_proximity,
                'default_arrival_buffer_minutes': self.optimization.default_arrival_buffer_minutes,
                'max_route_duration_minutes': self.optimization.max_route_duration_minutes,
                'max_clients_per_driver': self.optimization.max_clients_per_driver,
                'solver_timeout_seconds': self.optimization.solver_timeout_seconds,
                'enable_partial_reoptimization': self.optimization.enable_partial_reoptimization
            },
            'system': {
                'raw_file_retention_days': self.system.raw_file_retention_days,
                'max_drivers': self.system.max_drivers,
                'max_clients_per_day': self.system.max_clients_per_day,
                'scheduling_timeout_minutes': self.system.scheduling_timeout_minutes,
                'encrypt_data_at_rest': self.system.encrypt_data_at_rest,
                'require_authentication': self.system.require_authentication,
                'data_directory': self.system.data_directory,
                'drivers_file': self.system.drivers_file,
                'schedules_directory': self.system.schedules_directory,
                'cache_directory': self.system.cache_directory
            }
        }

