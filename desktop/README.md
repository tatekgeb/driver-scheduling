# Desktop Application

Electron-based desktop application for the Driver Scheduling System.

## Setup

1. Install dependencies:
```bash
npm install
```

2. Build React app:
```bash
npm run build:react
```

3. Run in development:
```bash
npm run dev
```

## Development

- **React + TypeScript**: Frontend UI
- **Webpack**: Bundling
- **Electron**: Desktop framework
- **IPC**: Communication with Python backend

## Building

Build for production:
```bash
npm run build
```

Build for specific platform:
```bash
npm run build:win
npm run build:mac
npm run build:linux
```

## Project Structure

```
desktop/
├── src/
│   ├── components/     # React components
│   │   ├── DriverForm.tsx
│   │   └── RouteView.tsx
│   ├── pages/         # Application pages
│   │   ├── DashboardPage.tsx
│   │   ├── DriversPage.tsx
│   │   ├── ImportPage.tsx
│   │   └── SchedulePage.tsx
│   ├── services/      # API services
│   │   └── api.ts
│   ├── styles/        # Global styles
│   │   └── global.css
│   ├── App.tsx        # Main app component
│   └── index.tsx       # Entry point
├── main.js            # Electron main process
├── webpack.config.js  # Webpack configuration
└── tsconfig.json      # TypeScript configuration
```

## Features

- **Dashboard**: Overview and quick actions
- **Driver Management**: CRUD operations for drivers
- **CSV Import**: Import and validate client data
- **Schedule Generation**: Generate optimized schedules
- **Schedule Visualization**: View routes and stops
- **Export**: Export schedules to CSV

