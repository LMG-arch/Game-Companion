// frontend/renderer/modules/click-through.js
/**
 * 点击穿透模块
 * 面板打开时禁用穿透，面板关闭时恢复穿透
 */

class ClickThrough {
  constructor() {
    this.isIgnoreMouse = true;
  }

  init() {
    // 初始状态：穿透
    this._setIgnoreMouse(true);
  }

  /**
   * 禁用穿透（面板打开时调用）
   */
  disable() {
    if (this.isIgnoreMouse) {
      this.isIgnoreMouse = false;
      this._setIgnoreMouse(false);
    }
  }

  /**
   * 恢复穿透（面板关闭时调用）
   */
  enable() {
    if (!this.isIgnoreMouse) {
      this.isIgnoreMouse = true;
      this._setIgnoreMouse(true);
    }
  }

  /**
   * 设置点击穿透
   */
  _setIgnoreMouse(ignore) {
    if (window.electronAPI) {
      window.electronAPI.send('set-ignore-mouse-events', ignore, ignore ? { forward: true } : {});
    }
  }
}

// 导出单例
window.clickThrough = new ClickThrough();
