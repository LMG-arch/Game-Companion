// frontend/renderer/modules/click-through.js
/**
 * 点击穿透模块
 * 使用 CSS pointer-events 控制穿透，而非 setIgnoreMouseEvents
 * 窗口始终接收鼠标事件，通过 CSS 控制哪些区域可点击
 */

class ClickThrough {
  constructor() {
    this.interactiveElements = [];
    this.overlay = null;
  }

  init() {
    // 创建全屏透明覆盖层，用于捕获鼠标事件并判断是否在交互区域
    this.overlay = document.createElement('div');
    this.overlay.id = 'click-through-overlay';
    this.overlay.style.cssText = `
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      z-index: 0;
      pointer-events: auto;
    `;
    document.body.insertBefore(this.overlay, document.body.firstChild);

    // 点击覆盖层时，检查是否在交互区域
    this.overlay.addEventListener('click', (e) => {
      if (this._isOverInteractive(e.clientX, e.clientY)) {
        // 在交互区域内，让事件穿透到实际元素
        this.overlay.style.pointerEvents = 'none';
        // 重新触发点击
        const target = document.elementFromPoint(e.clientX, e.clientY);
        if (target && target !== this.overlay) {
          target.click();
        }
        this.overlay.style.pointerEvents = 'auto';
      }
      // 不在交互区域内，点击穿透到游戏
    });

    // 鼠标移动时更新光标样式
    this.overlay.addEventListener('mousemove', (e) => {
      if (this._isOverInteractive(e.clientX, e.clientY)) {
        this.overlay.style.cursor = 'pointer';
      } else {
        this.overlay.style.cursor = 'default';
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
   * 检查坐标是否在交互区域上
   */
  _isOverInteractive(x, y) {
    for (const el of this.interactiveElements) {
      if (el.classList.contains('hidden') || el.style.display === 'none') {
        continue;
      }

      const rect = el.getBoundingClientRect();
      if (x >= rect.left && x <= rect.right && y >= rect.top && y <= rect.bottom) {
        return true;
      }
    }
    return false;
  }
}

// 导出单例
window.clickThrough = new ClickThrough();
