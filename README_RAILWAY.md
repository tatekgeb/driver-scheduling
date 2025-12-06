# Driver Scheduling System - Railway Web Application

This is a web-based driver scheduling system deployed on Railway, replacing the original Electron desktop application.

## Key Features

✅ **Web-based**: Accessible from any browser, no installation required  
✅ **Role-based Access**: Admin/dispatch and driver roles with appropriate permissions  
✅ **Schedule Printing**: Drivers can print their schedules with Graceconnections logo  
✅ **Optimized Scheduling**: Admin can run the optimization engine to generate optimal schedules  
✅ **Driver Isolation**: Drivers can only see and print their own schedules  

## Quick Start

### For Admin/Dispatch

1. Login with credentials:
   - Username: `admin`
   - Password: `admin123` (change immediately!)

2. **Import Client Data**:
   - Go to "Import Clients" page
   - Upload CSV file with client trip data
   - Select service date

3. **Generate Schedule**:
   - Go to "Schedule" page
   - Select service date
   - Click "Generate Schedule"
   - System will optimize driver assignments

### For Drivers

1. Login with your driver credentials:
   - Username: `driver_[your_driver_id]`
   - Password: `driver_[your_driver_id]` (change after first login!)

2. **View Schedule**:
   - Go to "My Schedule" page
   - Select date to view your schedule
   - Click "Print Schedule" to print with company logo

## Architecture

- **Backend**: Flask (Python) API server
- **Frontend**: React web application
- **Hosting**: Railway cloud platform
- **Database**: File-based storage (JSON files)

## Development

### Local Development

1. **Start Backend**:
```bash
cd api
pip install -r requirements.txt
python app.py
```

2. **Start Frontend** (in another terminal):
```bash
cd desktop
npm install
npm run dev
```

3. Access at `http://localhost:3000`

### Building for Production

```bash
cd desktop
npm run build:react
```

The built files will be in `desktop/dist/` and served by the Flask app.

## Deployment

See `RAILWAY_DEPLOYMENT.md` for detailed deployment instructions.

## Security

- Change default passwords immediately
- Use strong `SECRET_KEY` in production
- Consider implementing database-backed user management
- Enable HTTPS (Railway provides this automatically)

