// frontend/main/ipc.js
/**
 * IPC 通信层
 * 主进程与渲染进程之间的通信
 */

const { ipcMain } = require('electron');

class IPC {
  constructor() {
    this.handlers = {};
  }

  /**
   * 注册 IPC 处理器
   * @param {string} channel - 通道名
   * @param {function} handler - 处理函数
   */
  on(channel, handler) {
    ipcMain.on(channel, (event, ...args) => {
      try {
        handler(event, ...args);
      } catch (e) {
        console.error(`IPC 处理错误 [${channel}]:`, e);
      }
    });
    this.handlers[channel] = handler;
  }

  /**
   * 向渲染进程发送消息
   * @param {BrowserWindow} win - 窗口实例
   * @param {string} channel - 通道名
   * @param {any} data - 数据
   */
  send(win, channel, data) {
    if (win && win.webContents) {
      win.webContents.send(channel, data);
    }
  }
}

module.exports = IPC;
