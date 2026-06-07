// frontend/renderer/modules/click-through.js
/**
 * 点击穿透模块
 * 使用引用计数管理多个组件的穿透状态
 */

class ClickThrough {
  constructor() {
    this.isIgnoreMouse = true;
    this._disableCount = 0;
  }

  init() {
    // 初始状态：穿透
    this._setIgnoreMouse(true);
  }

  /**
   * 禁用穿透（引用计数 +1）
   */
  disable() {
    this._disableCount++;
    if (this.isIgnoreMouse) {
      this.isIgnoreMouse = false;
      this._setIgnoreMouse(false);
    }
  }

  /**
   * 恢复穿透（引用计数 -1，归零时才真正恢复）
   */
  enable() {
    this._disableCount = Math.max(0, this._disableCount - 1);
    if (this._disableCount === 0 && !this.isIgnoreMouse) {
      this.isIgnoreMouse = true;
      this._setIgnoreMouse(true);
    }
  }

  /**
   * 强制恢复穿透（忽略引用计数，用于面板关闭时）
   */
  forceEnable() {
    this._disableCount = 0;
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
