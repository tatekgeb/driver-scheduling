const { app, BrowserWindow, ipcMain, dialog } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const fs = require('fs');

// Python executable path
const PYTHON_EXE = process.env.PYTHON_PATH || 'C:\\Python312\\python.exe';
const PROJECT_ROOT = path.join(__dirname, '..');

function callPython(method, args = []) {
  return new Promise((resolve, reject) => {
    const scriptPath = path.join(PROJECT_ROOT, 'scripts', 'python_bridge.py');
    const process = spawn(PYTHON_EXE, [scriptPath, method, JSON.stringify(args)], {
      cwd: PROJECT_ROOT,
      stdio: ['pipe', 'pipe', 'pipe']
    });

    let output = '';
    let errorOutput = '';

    process.stdout.on('data', (data) => {
      output += data.toString();
    });

    process.stderr.on('data', (data) => {
      errorOutput += data.toString();
    });

    process.on('close', (code) => {
      if (code === 0) {
        try {
          const result = JSON.parse(output.trim());
          if (result.error) {
            reject(new Error(result.error));
          } else {
            resolve(result);
          }
        } catch (e) {
          reject(new Error(`Failed to parse Python output: ${e.message}\nOutput: ${output}`));
        }
      } else {
        reject(new Error(`Python process failed with code ${code}: ${errorOutput || output}`));
      }
    });

    process.on('error', (error) => {
      reject(new Error(`Failed to start Python process: ${error.message}`));
    });
  });
}

function createWindow() {
  const win = new BrowserWindow({
    width: 1400,
    height: 900,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
      enableRemoteModule: true
    }
  });

  // Load the React app
  const isDev = process.env.NODE_ENV === 'development';
  
  // Check if dist/index.html exists, otherwise use the old index.html
  const distPath = path.join(__dirname, 'dist', 'index.html');
  const oldPath = path.join(__dirname, 'index.html');
  
  if (fs.existsSync(distPath)) {
    win.loadFile(distPath);
  } else if (fs.existsSync(oldPath)) {
    win.loadFile(oldPath);
  } else {
    // Create a simple HTML file if neither exists
    win.loadURL('data:text/html,<h1>Building React app...</h1><p>Please run: npm run build:react</p>');
  }

  // Open DevTools in development
  if (isDev || process.argv.includes('--dev')) {
    win.webContents.openDevTools();
  }
}

// IPC Handlers
ipcMain.handle('api:getDrivers', async () => {
  try {
    return await callPython('getDrivers');
  } catch (error) {
    console.error('Error getting drivers:', error);
    return [];
  }
});

ipcMain.handle('api:createDriver', async (event, driver) => {
  try {
    return await callPython('createDriver', [driver]);
  } catch (error) {
    console.error('Error creating driver:', error);
    throw error;
  }
});

ipcMain.handle('api:updateDriver', async (event, driverId, driver) => {
  try {
    return await callPython('updateDriver', [driverId, driver]);
  } catch (error) {
    console.error('Error updating driver:', error);
    throw error;
  }
});

ipcMain.handle('api:deleteDriver', async (event, driverId) => {
  try {
    const result = await callPython('deleteDriver', [driverId]);
    return result.success || false;
  } catch (error) {
    console.error('Error deleting driver:', error);
    throw error;
  }
});

ipcMain.handle('api:importCSV', async (event, filePath, serviceDate) => {
  try {
    return await callPython('importCSV', [filePath, serviceDate]);
  } catch (error) {
    console.error('Error importing CSV:', error);
    throw error;
  }
});

ipcMain.handle('api:generateSchedule', async (event, serviceDate, tripIds, lockedAssignments) => {
  try {
    return await callPython('generateSchedule', [serviceDate, tripIds, lockedAssignments || {}]);
  } catch (error) {
    console.error('Error generating schedule:', error);
    throw error;
  }
});

ipcMain.handle('api:getSchedule', async (event, scheduleId) => {
  try {
    return await callPython('getSchedule', [scheduleId]);
  } catch (error) {
    console.error('Error getting schedule:', error);
    throw error;
  }
});

ipcMain.handle('api:reassignTrip', async (event, tripId, driverId) => {
  try {
    return await callPython('reassignTrip', [tripId, driverId]);
  } catch (error) {
    console.error('Error reassigning trip:', error);
    throw error;
  }
});

ipcMain.handle('api:exportScheduleToCSV', async (event, scheduleId, outputPath) => {
  try {
    await callPython('exportScheduleToCSV', [scheduleId, outputPath]);
  } catch (error) {
    console.error('Error exporting schedule:', error);
    throw error;
  }
});

// Dialog handlers
ipcMain.handle('dialog:showOpenDialog', async (event, options) => {
  const result = await dialog.showOpenDialog(options);
  return result;
});

ipcMain.handle('dialog:showSaveDialog', async (event, options) => {
  const result = await dialog.showSaveDialog(options);
  return result;
});

app.whenReady().then(() => {
  createWindow();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});
