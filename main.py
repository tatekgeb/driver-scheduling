"""
Main entry point for the Driver Scheduling System
"""
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from config.config import Config
from storage.driver_manager import DriverManager
from etl.csv_ingestion import ingest_client_csv
from engine.mapping_service import MappingService
from engine.optimizer import Optimizer
from shared.types.models import TripStatus


class SchedulingSystem:
    """Main application class"""
    
    def __init__(self, config_path: str = "config/config.json"):
        self.config = Config.from_file(config_path) if Path(config_path).exists() else Config()
        self.driver_manager = DriverManager(
            storage_path=f"{self.config.system.data_directory}/{self.config.system.drivers_file}"
        )
        self.mapping_service = MappingService(self.config.mapping_api)
        self.optimizer = Optimizer(self.config.optimization, self.mapping_service)
    
    def import_client_csv(self, csv_path: str, service_date: str) -> tuple:
        """
        Import client trips from CSV
        
        Returns:
            Tuple of (trips, errors)
        """
        trips, errors = ingest_client_csv(csv_path, self.config.optimization.default_arrival_buffer_minutes)
        
        # Mark trips as ready for scheduling
        for trip in trips:
            trip.status = TripStatus.READY_FOR_SCHEDULING
        
        return trips, errors
    
    def generate_schedule(self, service_date, trips, locked_assignments=None):
        """Generate optimized schedule"""
        drivers = self.driver_manager.get_all_drivers()
        return self.optimizer.optimize_schedule(service_date, drivers, trips, locked_assignments)


if __name__ == "__main__":
    print("Driver Scheduling System")
    print("=" * 50)
    print("\nThis is the main entry point.")
    print("Use the desktop application or import this module in your scripts.")
    print("\nExample usage:")
    print("  from main import SchedulingSystem")
    print("  system = SchedulingSystem()")
    print("  trips, errors = system.import_client_csv('data/clients.csv', '2024-12-01')")

