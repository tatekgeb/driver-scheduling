#!/usr/bin/env python3
"""
Script to get drivers for Electron IPC
"""
import sys
import json
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from main import SchedulingSystem

try:
    system = SchedulingSystem()
    drivers = system.driver_manager.get_all_drivers()
    
    result = []
    for d in drivers:
        result.append({
            'driver_id': d.driver_id,
            'name': d.name,
            'home_address': {
                'street_number': d.home_address.street_number,
                'street': d.home_address.street,
                'city': d.home_address.city,
                'state': d.home_address.state,
                'zip_code': d.home_address.zip_code,
                'full_address': str(d.home_address),
                'latitude': d.home_address.latitude,
                'longitude': d.home_address.longitude
            },
            'phone': d.phone,
            'vehicle_type': d.vehicle_type,
            'capacity': d.capacity,
            'service_days': d.service_days,
            'daily_start_time': d.daily_start_time.isoformat() if d.daily_start_time else None,
            'daily_end_time': d.daily_end_time.isoformat() if d.daily_end_time else None,
            'max_daily_distance': d.max_daily_distance,
            'max_daily_duration': d.max_daily_duration
        })
    
    print(json.dumps(result))
except Exception as e:
    print(json.dumps({'error': str(e)}), file=sys.stderr)
    sys.exit(1)

