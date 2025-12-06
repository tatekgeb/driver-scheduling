# Driver-Client Scheduling System

A desktop application for dispatchers to automatically generate optimized daily schedules assigning multiple drivers to clients who require transportation from their homes to medical appointments and back.

## Features

- **CSV Ingestion**: Import client trip data from CSV files with validation
- **Driver Management**: CRUD operations for driver information (home addresses, availability, constraints)
- **Geocoding**: Automatic address geocoding with caching
- **Route Optimization**: Vehicle Routing Problem with Time Windows (VRPTW) solver
- **Traffic-Aware Routing**: Uses mapping APIs for distance and time calculations with traffic patterns
- **Schedule Visualization**: View and edit driver schedules
- **Manual Adjustments**: Reassign clients, lock assignments, and re-optimize
- **Export**: Export schedules to CSV

## Project Structure

```
driver-scheduling/
├── desktop/              # Electron-based desktop application
│   ├── src/
│   │   ├── components/   # React components
│   │   ├── pages/       # Application pages
│   │   ├── services/    # API/service layer
│   │   └── utils/       # Utility functions
│   ├── main.js          # Electron main process
│   └── package.json
├── etl/                  # ETL processing module
│   ├── csv_ingestion.py  # CSV import and validation
│   └── process_csv.py   # Legacy CSV processor
├── engine/               # Optimization engine
│   ├── mapping_service.py # Geocoding and routing
│   └── optimizer.py      # VRPTW solver
├── storage/              # Data storage layer
│   └── driver_manager.py # Driver CRUD operations
├── config/               # Configuration management
│   ├── config.py        # Configuration classes
│   └── config.json      # Configuration file
├── shared/               # Shared code
│   ├── types/           # Data models
│   │   └── models.py    # Driver, ClientTrip, Route, Schedule models
│   └── utils/           # Shared utilities
├── docs/                 # Documentation
└── main.py              # Main application entry point
```

## Technology Stack

- **Desktop App**: Electron 39.2.4 + React 19.2.0 + TypeScript
- **ETL Processing**: Python 3.12+ with pandas 2.3.3, numpy 2.3.5
- **Mapping API**: Google Maps API (configurable)
- **Optimization**: Custom VRPTW solver (can be enhanced with OR-Tools)

## Getting Started

### Prerequisites

- Node.js 18+ and npm
- Python 3.12+
- Google Maps API key (for geocoding and routing)
- Git

### Installation

1. **Install desktop app dependencies:**
```bash
cd desktop
npm install
```

2. **Install Python dependencies:**
```bash
cd etl
# Windows (using Python at C:\Python312):
C:\Python312\python.exe -m pip install --user -r requirements.txt

# Or if Python is in PATH:
pip install -r requirements.txt
```

3. **Configure the system:**
   - Copy `config/config.json` and set your Google Maps API key
   - Set `MAPS_API_KEY` environment variable, or edit `config/config.json`

### Development

**Start the desktop application:**
```bash
cd desktop
npm run dev
```

**Run ETL processing:**
```bash
cd etl
python csv_ingestion.py input_file.csv
```

## Usage

### 1. Import Client Data

Upload a CSV file with client trip information. Expected columns:
- Customer Number
- Passenger Name
- Trip Date
- Promised pick-up time
- Pickup street number, Pickup Street, Pickup City
- Promised drop-off time
- Drop-off street number, Drop-off Street, Drop-off City
- Mobility Needs (optional)
- Special Notes (optional)
- Hard Driver Constraints (optional)

### 2. Manage Drivers

Add drivers with:
- Home address (will be geocoded automatically)
- Service days and hours
- Vehicle information
- Constraints (max distance, max duration)

### 3. Generate Schedule

Select a service date and run the optimization engine. The system will:
- Geocode all addresses
- Calculate travel times with traffic
- Assign clients to drivers optimally
- Generate routes with timestamps

### 4. Review and Adjust

- View schedules per driver
- Manually reassign clients
- Lock assignments
- Re-optimize remaining trips

### 5. Export

Export driver schedules to CSV for distribution.

## Configuration

Edit `config/config.json` to configure:

- **Mapping API**: Provider, API key, traffic settings, caching
- **Optimization**: Objective weights, constraints, solver settings
- **System**: Data retention, performance limits, security settings

## Data Models

### Driver
- Driver ID, name, home address
- Availability (service days, start/end times)
- Vehicle information
- Constraints (max distance, max duration)

### ClientTrip
- Customer information
- Pickup and dropoff addresses
- Time windows (pickup time, appointment time)
- Special requirements
- Status (imported, ready, scheduled, invalid)

### Route
- Driver assignment
- Ordered list of stops (pickup/dropoff)
- Timestamps for each stop
- Total distance and time

### Schedule
- Service date
- All driver routes
- Unassigned trips (if any)

## API Integration

### Google Maps API

The system uses Google Maps API for:
- **Geocoding**: Convert addresses to coordinates
- **Routing**: Calculate distance and travel time
- **Traffic**: Time-of-day aware traffic estimates

**Setup:**
1. Get API key from [Google Cloud Console](https://console.cloud.google.com/)
2. Enable Geocoding API and Directions API
3. Set API key in configuration

## Optimization Algorithm

The system solves a Vehicle Routing Problem with Time Windows (VRPTW):
- **Objective**: Minimize total travel time/distance
- **Constraints**: 
  - Time windows (pickup and appointment times)
  - Driver availability
  - Route feasibility
- **Algorithm**: Greedy assignment with cost optimization

**Note**: The current implementation uses a simplified greedy algorithm. For production use with large datasets, consider integrating a more sophisticated solver like:
- Google OR-Tools
- Gurobi Optimizer
- CPLEX

## Security

- Client data (names, addresses, health information) is sensitive
- Secure storage (encrypted at rest, secure transport)
- Role-based access control (planned)

## Performance

Designed to handle:
- Up to 50 drivers
- Up to 500 clients per day
- Scheduling runs complete within 5-10 minutes

## Development Status

🚧 **Active Development**

- [x] Project structure
- [x] Data models
- [x] CSV ingestion with validation
- [x] Driver management (CRUD)
- [x] Geocoding service
- [x] Basic optimization engine
- [ ] Desktop UI (React + Electron)
- [ ] Schedule visualization
- [ ] Manual adjustments
- [ ] Export functionality
- [ ] Advanced optimization solver

## License

ISC

## Support

For issues and questions, please refer to the documentation in the `docs/` directory.
