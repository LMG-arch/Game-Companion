// frontend/renderer/modules/click-through.js
/**
 * 点击穿透模块
 * 使用 mousemove 检测鼠标是否在交互区域上
 */

class ClickThrough {
  constructor() {
    this.interactiveElements = [];
    this.isOverInteractive = false;
  }

  init() {
    // 监听鼠标移动（forward: true 时会触发）
    document.addEventListener('mousemove', (e) => {
      this._checkMousePosition(e.clientX, e.clientY);
    });

    // 鼠标离开窗口时恢复穿透
    document.addEventListener('mouseleave', () => {
      if (this.isOverInteractive) {
        this.isOverInteractive = false;
        this._setIgnoreMouse(true);
      }
    });
  }

  /**
   * 注册可交互元素
   * @param {HTMLElement} element
   */
  register(element) {
    if (element && !this.interactiveElements.includes(element)) {
      this.interactiveElements.push(element);
    }
  }

  /**
   * 检查鼠标是否在交互区域上
   */
  _checkMousePosition(x, y) {
    let overInteractive = false;

    for (const el of this.interactiveElements) {
      if (el.classList.contains('hidden') || el.style.display === 'none') {
        continue;
      }

      const rect = el.getBoundingClientRect();
      if (x >= rect.left && x <= rect.right && y >= rect.top && y <= rect.bottom) {
        overInteractive = true;
        break;
      }
    }

    if (overInteractive !== this.isOverInteractive) {
      this.isOverInteractive = overInteractive;
      this._setIgnoreMouse(!overInteractive);
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
