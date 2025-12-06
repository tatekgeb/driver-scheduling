"""
Flask API server for Driver Scheduling System
Replaces Electron IPC communication with HTTP API
"""
import os
import json
from datetime import datetime
from pathlib import Path
from flask import Flask, request, jsonify, send_file, session
from flask_cors import CORS
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps
import sys

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from main import SchedulingSystem
from shared.types.models import Driver, Address, TripStatus
from storage.trip_storage import TripStorage
from storage.schedule_manager import ScheduleManager
from scripts.python_bridge import serialize_driver, serialize_trip, serialize_route, serialize_schedule, deserialize_driver

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
CORS(app, supports_credentials=True)

# Change working directory to project root to ensure all relative paths work correctly
import os
os.chdir(PROJECT_ROOT)

# Initialize system (all paths will now resolve relative to project root)
scheduling_system = SchedulingSystem()
trip_storage = TripStorage()
schedule_manager = ScheduleManager()

# Simple user storage (in production, use a database)
# Format: {username: {password_hash, role, driver_id}}
USERS = {
    'admin': {
        'password_hash': generate_password_hash('admin123'),  # Change in production
        'role': 'admin',
        'driver_id': None
    }
}

# Load users from environment or config
def load_users():
    """Load users from environment variables or config file"""
    # In production, load from database or environment
    # For now, we'll add drivers as users when they're created
    pass

# Authentication decorators
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        if session.get('role') != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        return f(*args, **kwargs)
    return decorated_function

# Authentication endpoints
@app.route('/api/auth/login', methods=['POST'])
def login():
    """Login endpoint"""
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'error': 'Username and password required'}), 400
    
    # Check if user exists
    user = USERS.get(username)
    if not user:
        return jsonify({'error': 'Invalid credentials'}), 401
    
    if not check_password_hash(user['password_hash'], password):
        return jsonify({'error': 'Invalid credentials'}), 401
    
    session['user_id'] = username
    session['role'] = user['role']
    session['driver_id'] = user.get('driver_id')
    
    return jsonify({
        'user_id': username,
        'role': user['role'],
        'driver_id': user.get('driver_id')
    })

@app.route('/api/auth/logout', methods=['POST'])
def logout():
    """Logout endpoint"""
    session.clear()
    return jsonify({'message': 'Logged out successfully'})

@app.route('/api/auth/me', methods=['GET'])
@login_required
def get_current_user():
    """Get current user info"""
    return jsonify({
        'user_id': session.get('user_id'),
        'role': session.get('role'),
        'driver_id': session.get('driver_id')
    })

# Driver endpoints
@app.route('/api/drivers', methods=['GET'])
@login_required
def get_drivers():
    """Get all drivers (admin only) or current driver"""
    role = session.get('role')
    driver_id = session.get('driver_id')
    
    if role == 'admin':
        drivers = scheduling_system.driver_manager.get_all_drivers()
        return jsonify([serialize_driver(d) for d in drivers])
    elif role == 'driver' and driver_id:
        driver = scheduling_system.driver_manager.get_driver(driver_id)
        if driver:
            return jsonify([serialize_driver(driver)])
        return jsonify([])
    else:
        return jsonify({'error': 'Access denied'}), 403

@app.route('/api/drivers', methods=['POST'])
@admin_required
def create_driver():
    """Create a new driver"""
    driver_data = request.json
    driver = deserialize_driver(driver_data)
    created = scheduling_system.driver_manager.create_driver(driver)
    
    # Create user account for driver
    username = f"driver_{created.driver_id}"
    USERS[username] = {
        'password_hash': generate_password_hash(f"driver_{created.driver_id}"),  # Default password
        'role': 'driver',
        'driver_id': created.driver_id
    }
    
    return jsonify(serialize_driver(created)), 201

@app.route('/api/drivers/<driver_id>', methods=['PUT'])
@admin_required
def update_driver(driver_id):
    """Update a driver"""
    driver_data = request.json
    driver = deserialize_driver(driver_data)
    updated = scheduling_system.driver_manager.update_driver(driver_id, driver)
    return jsonify(serialize_driver(updated))

@app.route('/api/drivers/<driver_id>', methods=['DELETE'])
@admin_required
def delete_driver(driver_id):
    """Delete a driver"""
    result = scheduling_system.driver_manager.delete_driver(driver_id)
    
    # Remove user account
    username = f"driver_{driver_id}"
    if username in USERS:
        del USERS[username]
    
    return jsonify({'success': result})

# CSV Import endpoint
@app.route('/api/import/csv', methods=['POST'])
@admin_required
def import_csv():
    """Import client trips from CSV"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    service_date = request.form.get('service_date')
    
    if not service_date:
        return jsonify({'error': 'Service date required'}), 400
    
    # Save uploaded file temporarily
    upload_path = PROJECT_ROOT / 'data' / 'uploads'
    upload_path.mkdir(parents=True, exist_ok=True)
    file_path = upload_path / file.filename
    file.save(str(file_path))
    
    try:
        trips, errors = scheduling_system.import_client_csv(str(file_path), service_date)
        trip_storage.save_trips(service_date, trips)
        
        result = {
            'trips': [serialize_trip(t) for t in trips],
            'errors': [{
                'row_number': e.row_number,
                'field': e.field,
                'error_description': e.error_description
            } for e in errors]
        }
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        # Clean up uploaded file
        if file_path.exists():
            file_path.unlink()

# Schedule endpoints
@app.route('/api/schedules/generate', methods=['POST'])
@admin_required
def generate_schedule():
    """Generate optimized schedule"""
    data = request.json
    service_date_str = data.get('service_date')
    trip_ids = data.get('trip_ids', [])
    locked_assignments = data.get('locked_assignments', {})
    
    if not service_date_str:
        return jsonify({'error': 'Service date required'}), 400
    
    try:
        service_date = datetime.fromisoformat(service_date_str)
        
        # Get trips from storage
        if trip_ids:
            trips = trip_storage.get_trips_by_ids(service_date_str, trip_ids)
        else:
            trips = trip_storage.get_trips_for_date(service_date_str)
        
        if not trips:
            return jsonify({'error': 'No trips found for this service date. Please import client data first.'}), 400
        
        schedule = scheduling_system.generate_schedule(service_date, trips, locked_assignments)
        schedule_manager.save_schedule(schedule)
        
        return jsonify(serialize_schedule(schedule))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/schedules/<schedule_id>', methods=['GET'])
@login_required
def get_schedule(schedule_id):
    """Get schedule by ID"""
    role = session.get('role')
    driver_id = session.get('driver_id')
    
    schedule = schedule_manager.get_schedule(schedule_id)
    if not schedule:
        return jsonify({'error': 'Schedule not found'}), 404
    
    # Drivers can only see their own route
    if role == 'driver' and driver_id:
        schedule.routes = [r for r in schedule.routes if r.driver_id == driver_id]
        schedule.unassigned_trips = []  # Don't show unassigned to drivers
    
    return jsonify(serialize_schedule(schedule))

@app.route('/api/schedules', methods=['GET'])
@login_required
def list_schedules():
    """List schedules for a service date"""
    service_date = request.args.get('service_date')
    role = session.get('role')
    driver_id = session.get('driver_id')
    
    if not service_date:
        return jsonify({'error': 'Service date required'}), 400
    
    # Find all schedule files for this date
    schedules_dir = PROJECT_ROOT / 'data' / 'schedules'
    schedules = []
    
    for schedule_file in schedules_dir.glob('*.json'):
        try:
            with open(schedule_file, 'r') as f:
                schedule_data = json.load(f)
                if schedule_data.get('service_date', '').startswith(service_date):
                    schedule = schedule_manager.get_schedule(schedule_data['schedule_id'])
                    if schedule:
                        # Filter for driver if needed
                        if role == 'driver' and driver_id:
                            schedule.routes = [r for r in schedule.routes if r.driver_id == driver_id]
                            schedule.unassigned_trips = []
                            if not schedule.routes:
                                continue  # Skip if no routes for this driver
                        
                        schedules.append(serialize_schedule(schedule))
        except Exception as e:
            continue
    
    return jsonify(schedules)

@app.route('/api/schedules/<schedule_id>/driver/<driver_id>', methods=['GET'])
@login_required
def get_driver_schedule(schedule_id, driver_id):
    """Get a specific driver's route from a schedule"""
    role = session.get('role')
    current_driver_id = session.get('driver_id')
    
    # Drivers can only access their own schedule
    if role == 'driver' and current_driver_id != driver_id:
        return jsonify({'error': 'Access denied'}), 403
    
    schedule = schedule_manager.get_schedule(schedule_id)
    if not schedule:
        return jsonify({'error': 'Schedule not found'}), 404
    
    # Find the route for this driver
    driver_route = None
    for route in schedule.routes:
        if route.driver_id == driver_id:
            driver_route = route
            break
    
    if not driver_route:
        return jsonify({'error': 'No schedule found for this driver'}), 404
    
    return jsonify({
        'schedule_id': schedule.schedule_id,
        'service_date': schedule.service_date.isoformat(),
        'route': serialize_route(driver_route)
    })

# Export endpoint
@app.route('/api/schedules/<schedule_id>/export', methods=['GET'])
@admin_required
def export_schedule(schedule_id):
    """Export schedule to CSV"""
    schedule = schedule_manager.get_schedule(schedule_id)
    if not schedule:
        return jsonify({'error': 'Schedule not found'}), 404
    
    output_path = PROJECT_ROOT / 'data' / 'exports' / f"schedule_{schedule_id}.csv"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    schedule_manager.export_to_csv(schedule, str(output_path))
    
    return send_file(
        str(output_path),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f"schedule_{schedule.service_date.strftime('%Y-%m-%d')}.csv"
    )

# Serve React app in production
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_react_app(path):
    """Serve React app"""
    dist_path = PROJECT_ROOT / 'desktop' / 'dist'
    
    # Serve static files
    if path and not path.startswith('api'):
        file_path = dist_path / path
        if file_path.exists() and file_path.is_file():
            return send_file(str(file_path))
    
    # Serve index.html for all other routes (SPA routing)
    index_path = dist_path / 'index.html'
    if index_path.exists():
        return send_file(str(index_path))
    
    return jsonify({'error': 'Frontend not built. Run: cd desktop && npm run build:react'}), 404

if __name__ == '__main__':
    # Working directory should already be set to PROJECT_ROOT above
    port = int(os.environ.get('PORT', 5000))
    # In production, use a proper WSGI server
    if os.environ.get('RAILWAY_ENVIRONMENT'):
        from waitress import serve
        serve(app, host='0.0.0.0', port=port)
    else:
        app.run(host='0.0.0.0', port=port, debug=os.environ.get('FLASK_DEBUG', 'False') == 'True')

