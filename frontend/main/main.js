// frontend/main/main.js
/**
 * Electron 主进程入口
 * 创建透明覆盖窗口，管理 Python 子进程
 */

const { app, BrowserWindow, ipcMain, screen } = require('electron');
const path = require('path');
const PythonManager = require('./python-manager');
const Shortcuts = require('./shortcuts');

// Python 进程管理器
const pythonManager = new PythonManager();

// 快捷键管理
const shortcuts = new Shortcuts();

// 主窗口
let mainWindow = null;

/**
 * 创建透明覆盖窗口
 * 使用固定尺寸覆盖整个屏幕，避免 fullscreen 模式导致的窗口闪烁
 */
function createWindow() {
  const { width, height } = screen.getPrimaryDisplay().workAreaSize;

  mainWindow = new BrowserWindow({
    x: 0,
    y: 0,
    width: width,
    height: height,
    transparent: true,
    frame: false,
    alwaysOnTop: true,
    skipTaskbar: true,
    resizable: false,
    movable: false,
    hasShadow: false,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js'),
    }
  });

  mainWindow.loadFile(path.join(__dirname, '..', 'renderer', 'index.html'));

  // 不使用 setIgnoreMouseEvents，改用 CSS pointer-events 控制穿透
  // 窗口始终接收鼠标事件，body 默认 pointer-events: none 让点击穿透

  // 确保窗口始终在最上层
  mainWindow.setAlwaysOnTop(true, 'screen-saver');

  // 开发模式下打开 DevTools
  if (process.argv.includes('--dev')) {
    mainWindow.webContents.openDevTools({ mode: 'detach' });
  }

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

/**
 * 应用启动
 */
app.whenReady().then(async () => {
  console.log('Electron 已启动');

  // 启动 Python 子进程
  try {
    await pythonManager.start();
    const port = pythonManager.getPort();
    console.log(`Python 端口: ${port}`);

    // 创建窗口
    createWindow();

    // 注册快捷键
    shortcuts.register({
      toggleInput: () => {
        if (mainWindow) mainWindow.webContents.send('shortcut', 'toggle-input');
      },
      toggleUI: () => {
        if (mainWindow) mainWindow.webContents.send('shortcut', 'toggle-ui');
      },
      openSettings: () => {
        if (mainWindow) mainWindow.webContents.send('shortcut', 'open-settings');
      },
      toggleDanmaku: () => {
        if (mainWindow) mainWindow.webContents.send('shortcut', 'toggle-danmaku');
      }
    });

    // 通知渲染进程连接 WebSocket
    if (mainWindow) {
      mainWindow.webContents.on('did-finish-load', () => {
        mainWindow.webContents.send('python-ready', { port });
      });
    }
  } catch (e) {
    console.error('Python 启动失败:', e);
    app.quit();
  }
});

/**
 * 应用关闭
 */
app.on('window-all-closed', async () => {
  console.log('正在关闭...');
  shortcuts.unregisterAll();
  await pythonManager.shutdown();
  app.quit();
});

app.on('before-quit', async () => {
  shortcuts.unregisterAll();
  await pythonManager.shutdown();
});
