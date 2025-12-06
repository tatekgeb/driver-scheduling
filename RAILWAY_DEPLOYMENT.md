# Railway Deployment Guide

This guide explains how to deploy the Driver Scheduling System to Railway.

## Prerequisites

1. A Railway account (sign up at https://railway.app)
2. A GitHub repository with this code
3. Google Maps API key (for geocoding and routing)

## Deployment Steps

### 1. Connect Repository to Railway

1. Go to Railway dashboard
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Choose your repository

### 2. Configure Environment Variables

In Railway project settings, add these environment variables:

- `SECRET_KEY`: A random secret key for Flask sessions (generate with: `python -c "import secrets; print(secrets.token_hex(32))"`)
- `MAPS_API_KEY`: Your Google Maps API key
- `FLASK_DEBUG`: Set to `False` for production
- `PORT`: Railway will set this automatically, but you can set it to `5000` if needed

### 3. Build Configuration

Railway will automatically detect the `.nixpacks.toml` file and use it for building. The build process will:

1. Install Node.js 18
2. Install Python 3.12
3. Build the React frontend (`cd desktop && npm install && npm run build:react`)
4. Install Python dependencies (`pip install -r api/requirements.txt`)

### 4. Start Command

The start command is configured in `.nixpacks.toml`:
```
cd api && python app.py
```

This will start the Flask server which serves both the API and the React frontend.

## Post-Deployment

### Initial Admin Account

The default admin account is:
- Username: `admin`
- Password: `admin123`

**⚠️ IMPORTANT: Change this password immediately after first login!**

### Creating Driver Accounts

1. Login as admin
2. Go to Drivers page
3. Create a new driver
4. A driver account will be automatically created with:
   - Username: `driver_[driver_id]`
   - Password: `driver_[driver_id]` (same as username)

**⚠️ IMPORTANT: Drivers should change their passwords after first login!**

## Features

### Admin/Dispatch Features
- Manage drivers (CRUD operations)
- Import client data from CSV
- Generate optimized schedules
- View all schedules
- Export schedules to CSV

### Driver Features
- View their own schedule for any date
- Print schedule with Graceconnections logo
- Cannot see other drivers' schedules

## File Structure

```
driver-scheduling/
├── api/                    # Flask backend API
│   ├── app.py             # Main Flask application
│   └── requirements.txt   # Python dependencies
├── desktop/               # React frontend
│   ├── src/               # React source code
│   └── dist/              # Built React app (generated)
├── .nixpacks.toml        # Railway build configuration
├── Procfile              # Process file for Railway
└── runtime.txt           # Python version
```

## Troubleshooting

### Frontend not loading
- Ensure `desktop/dist` directory exists with built files
- Check that `npm run build:react` completed successfully during build

### API errors
- Check that all Python dependencies are installed
- Verify Google Maps API key is set correctly
- Check Railway logs for detailed error messages

### Authentication issues
- Ensure `SECRET_KEY` environment variable is set
- Clear browser cookies and try again

## Updating the Application

1. Push changes to GitHub
2. Railway will automatically detect changes and redeploy
3. Monitor the deployment logs in Railway dashboard

## Security Notes

- Change default admin password immediately
- Use strong `SECRET_KEY` in production
- Consider implementing proper user management with database
- Enable HTTPS (Railway provides this automatically)
- Regularly update dependencies

## Support

For issues or questions, check the main README.md file or contact support.

