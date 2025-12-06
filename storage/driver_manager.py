"""
Driver management module - CRUD operations for drivers
"""
import json
from typing import List, Optional
from pathlib import Path
from datetime import datetime

from shared.types.models import Driver, Address


class DriverManager:
    """Manages driver data (CRUD operations)"""
    
    def __init__(self, storage_path: str = "data/drivers.json"):
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self.drivers: List[Driver] = []
        self.load_drivers()
    
    def load_drivers(self):
        """Load drivers from storage"""
        if self.storage_path.exists():
            try:
                with open(self.storage_path, 'r') as f:
                    data = json.load(f)
                    self.drivers = [self._dict_to_driver(d) for d in data]
            except Exception as e:
                print(f"Error loading drivers: {e}")
                self.drivers = []
        else:
            self.drivers = []
    
    def save_drivers(self):
        """Save drivers to storage"""
        data = [self._driver_to_dict(d) for d in self.drivers]
        with open(self.storage_path, 'w') as f:
            json.dump(data, f, indent=2, default=str)
    
    def _driver_to_dict(self, driver: Driver) -> dict:
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
                'full_address': driver.home_address.full_address,
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
    
    def _dict_to_driver(self, data: dict) -> Driver:
        """Convert dictionary to Driver object"""
        from datetime import time as dt_time
        
        # Parse address
        addr_data = data.get('home_address', {})
        address = Address(
            street_number=addr_data.get('street_number', ''),
            street=addr_data.get('street', ''),
            city=addr_data.get('city', ''),
            state=addr_data.get('state'),
            zip_code=addr_data.get('zip_code'),
            full_address=addr_data.get('full_address'),
            latitude=addr_data.get('latitude'),
            longitude=addr_data.get('longitude')
        )
        
        # Parse time objects
        start_time = None
        if data.get('daily_start_time'):
            time_parts = data['daily_start_time'].split(':')
            start_time = dt_time(int(time_parts[0]), int(time_parts[1]))
        
        end_time = None
        if data.get('daily_end_time'):
            time_parts = data['daily_end_time'].split(':')
            end_time = dt_time(int(time_parts[0]), int(time_parts[1]))
        
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
    
    def create_driver(self, driver: Driver) -> Driver:
        """Create a new driver"""
        # Check if driver_id already exists
        if any(d.driver_id == driver.driver_id for d in self.drivers):
            raise ValueError(f"Driver with ID {driver.driver_id} already exists")
        
        self.drivers.append(driver)
        self.save_drivers()
        return driver
    
    def get_driver(self, driver_id: str) -> Optional[Driver]:
        """Get driver by ID"""
        for driver in self.drivers:
            if driver.driver_id == driver_id:
                return driver
        return None
    
    def get_all_drivers(self) -> List[Driver]:
        """Get all drivers"""
        return self.drivers.copy()
    
    def update_driver(self, driver_id: str, updated_driver: Driver) -> Driver:
        """Update an existing driver"""
        for i, driver in enumerate(self.drivers):
            if driver.driver_id == driver_id:
                if updated_driver.driver_id != driver_id:
                    # Check if new ID conflicts
                    if any(d.driver_id == updated_driver.driver_id for d in self.drivers if d.driver_id != driver_id):
                        raise ValueError(f"Driver with ID {updated_driver.driver_id} already exists")
                self.drivers[i] = updated_driver
                self.save_drivers()
                return updated_driver
        
        raise ValueError(f"Driver with ID {driver_id} not found")
    
    def delete_driver(self, driver_id: str) -> bool:
        """Delete a driver"""
        for i, driver in enumerate(self.drivers):
            if driver.driver_id == driver_id:
                del self.drivers[i]
                self.save_drivers()
                return True
        return False
    
    def export_to_csv(self, output_path: str):
        """Export drivers to CSV"""
        import pandas as pd
        
        data = []
        for driver in self.drivers:
            data.append({
                'Driver ID': driver.driver_id,
                'Name': driver.name,
                'Home Address': str(driver.home_address),
                'Phone': driver.phone or '',
                'Vehicle Type': driver.vehicle_type or '',
                'Capacity': driver.capacity or '',
                'Service Days': ', '.join(driver.service_days),
                'Daily Start Time': driver.daily_start_time.isoformat() if driver.daily_start_time else '',
                'Daily End Time': driver.daily_end_time.isoformat() if driver.daily_end_time else '',
                'Max Daily Distance': driver.max_daily_distance or '',
                'Max Daily Duration': driver.max_daily_duration or ''
            })
        
        df = pd.DataFrame(data)
        df.to_csv(output_path, index=False)
    
    def import_from_csv(self, csv_path: str):
        """Import drivers from CSV"""
        import pandas as pd
        from datetime import time as dt_time
        
        df = pd.read_csv(csv_path)
        
        for _, row in df.iterrows():
            # Parse address
            address_str = str(row.get('Home Address', ''))
            # Simple parsing - can be enhanced
            address = Address(
                street_number='',
                street='',
                city='',
                full_address=address_str
            )
            
            # Parse service days
            service_days = []
            if pd.notna(row.get('Service Days')):
                service_days = [d.strip() for d in str(row['Service Days']).split(',')]
            
            # Parse times
            start_time = None
            if pd.notna(row.get('Daily Start Time')):
                try:
                    time_str = str(row['Daily Start Time'])
                    parts = time_str.split(':')
                    start_time = dt_time(int(parts[0]), int(parts[1]))
                except:
                    pass
            
            end_time = None
            if pd.notna(row.get('Daily End Time')):
                try:
                    time_str = str(row['Daily End Time'])
                    parts = time_str.split(':')
                    end_time = dt_time(int(parts[0]), int(parts[1]))
                except:
                    pass
            
            # Parse active status
            active = True
            if pd.notna(row.get('Active')):
                active_str = str(row['Active']).strip().upper()
                active = active_str in ['YES', 'Y', 'TRUE', '1', 'ACTIVE']
            
            driver = Driver(
                driver_id=str(row['Driver ID']),
                name=str(row['Name']),
                home_address=address,
                phone=str(row.get('Phone', '')) if pd.notna(row.get('Phone')) else None,
                vehicle_type=str(row.get('Vehicle Type', '')) if pd.notna(row.get('Vehicle Type')) else None,
                capacity=int(row['Capacity']) if pd.notna(row.get('Capacity')) else None,
                active=active,
                service_days=service_days,
                daily_start_time=start_time,
                daily_end_time=end_time,
                max_daily_distance=float(row['Max Daily Distance']) if pd.notna(row.get('Max Daily Distance')) else None,
                max_daily_duration=int(row['Max Daily Duration']) if pd.notna(row.get('Max Daily Duration')) else None
            )
            
            # Create or update
            existing = self.get_driver(driver.driver_id)
            if existing:
                self.update_driver(driver.driver_id, driver)
            else:
                self.create_driver(driver)

