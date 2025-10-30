const { app, BrowserWindow } = require('electron');
const next = require('next');
const http = require('http');

const isDev = !app.isPackaged;
const nextApp = next({ dev: isDev, dir: './web' });
const handle = nextApp.getRequestHandler();

let server;

async function createWindow() {
  await nextApp.prepare();

  server = http.createServer((req, res) => handle(req, res));
  server.listen(3000);

  const win = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: { nodeIntegration: false },
  });

  win.loadURL('http://localhost:3000');
}

app.whenReady().then(createWindow);

app.on('window-all-closed', () => {
  if (server) server.close();
  if (process.platform !== 'darwin') app.quit();
});

