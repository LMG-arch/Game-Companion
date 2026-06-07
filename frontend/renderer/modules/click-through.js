// frontend/renderer/modules/click-through.js
/**
 * 点击穿透模块
 * 管理 4 种模式：全穿透/输入/设置/气泡交互
 */

class ClickThrough {
  constructor() {
    this.mode = 'full'; // full/input/settings/bubble
    this.ipcRenderer = null;
  }

  init(ipcRenderer) {
    this.ipcRenderer = ipcRenderer;
    this.setMode('full');
  }

  /**
   * 设置穿透模式
   * @param {string} mode - full/input/settings/bubble
   */
  setMode(mode) {
    this.mode = mode;

    if (!this.ipcRenderer) return;

    switch (mode) {
      case 'full':
        // 全穿透：所有鼠标事件穿透
        this.ipcRenderer.send('set-ignore-mouse-events', true, { forward: true });
        break;

      case 'input':
        // 输入模式：输入框可交互，其余穿透
        this.ipcRenderer.send('set-ignore-mouse-events', false);
        break;

      case 'settings':
        // 设置模式：整个面板可交互
        this.ipcRenderer.send('set-ignore-mouse-events', false);
        break;

      case 'bubble':
        // 气泡交互：气泡区域可交互，其余穿透
        this.ipcRenderer.send('set-ignore-mouse-events', true, { forward: true });
        break;
    }
  }

  getMode() {
    return this.mode;
  }
}

// 导出单例
window.clickThrough = new ClickThrough();
