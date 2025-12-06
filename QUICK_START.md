# Quick Start Guide

## Prerequisites

1. **Node.js 18+** installed
2. **Python 3.12** installed at `C:\Python312\` (or update path in `desktop/main.js`)
3. **Google Maps API Key** (optional, for geocoding and routing)

## Installation

### 1. Install Desktop App Dependencies
```bash
cd desktop
npm install
```

### 2. Install Python Dependencies
```bash
cd etl
C:\Python312\python.exe -m pip install --user -r requirements.txt
```

### 3. Build React App
```bash
cd desktop
npm run build:react
```

## Configuration

### Set Google Maps API Key (Optional)

1. Get API key from [Google Cloud Console](https://console.cloud.google.com/)
2. Enable "Geocoding API" and "Directions API"
3. Set in one of these ways:
   - Set environment variable: `MAPS_API_KEY=your_key_here`
   - Edit `config/config.json` and add API key to `mapping_api.api_key`

### Adjust Python Path (if needed)

If Python is not at `C:\Python312\python.exe`, edit `desktop/main.js`:
```javascript
const PYTHON_EXE = 'C:\\Your\\Python\\Path\\python.exe';
```

## Running the Application

```bash
cd desktop
npm run dev
```

## First Steps

1. **Add a Driver**:
   - Click "Drivers" in navigation
   - Click "Add Driver"
   - Fill in required fields (Driver ID, Name, Address)
   - Set service days and hours
   - Click "Create Driver"

2. **Import Client Data**:
   - Click "Import Clients"
   - Select service date
   - Click "Browse..." and select CSV file
   - Click "Import CSV"
   - Review any validation errors

3. **Generate Schedule**:
   - Click "Schedule"
   - Select service date (must match import date)
   - Click "Generate Schedule"
   - View routes and stops
   - Export to CSV if needed

## CSV Format

Your CSV file should have these columns:
- Customer Number
- Passenger Name
- Trip Date
- Promised pick-up time
- Pickup street number
- Pickup Street
- Pickup City
- Promised drop-off time
- Drop-off street number
- Drop-off Street
- Drop-off City
- Mobility Needs (optional)
- Special Notes (optional)
- Hard Driver Constraints (optional)

## Troubleshooting

### App opens but pages don't load
- Make sure you ran `npm run build:react`
- Check browser console (DevTools) for errors
- Verify `desktop/dist/index.html` exists

### Python errors
- Verify Python path in `desktop/main.js`
- Check that all Python dependencies are installed
- Look at Electron console for Python error messages

### Import fails
- Check CSV format matches expected columns
- Review validation errors in the UI
- Ensure service date matches trip dates in CSV

### Schedule generation fails
- Make sure you have drivers added
- Verify client data was imported for the service date
- Check that drivers have service days set
- Ensure Google Maps API key is set (for geocoding)

## Data Storage

All data is stored in the `data/` directory:
- `data/drivers.json` - Driver information
- `data/trips/YYYY-MM-DD.json` - Imported trips by date
- `data/schedules/` - Generated schedules
- `cache/geocoding/` - Cached geocoding results

## Development

### Rebuild React app after changes
```bash
cd desktop
npm run build:react
```

### Watch mode (auto-rebuild)
```bash
cd desktop
npm run watch:react
```

### Production build
```bash
cd desktop
npm run build
```

## Support

For issues, check:
- `INTEGRATION_COMPLETE.md` - Integration details
- `IMPLEMENTATION.md` - Implementation status
- `README.md` - Full documentation

