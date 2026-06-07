// frontend/renderer/components/DanmakuLayer.js
/**
 * 弹幕层组件（纯 DOM 容器）
 * 弹幕管理逻辑由 DanmakuEngine 处理
 */

class DanmakuLayer {
  constructor() {
    this.element = null;
    this.visible = true;
    this.init();
  }

  init() {
    this.element = document.createElement('div');
    this.element.id = 'danmaku-layer';
    this.element.style.cssText = `
      position: fixed;
      top: 50px;
      left: 0;
      right: 0;
      bottom: 50px;
      z-index: 20;
      pointer-events: none;
      overflow: hidden;
    `;

    document.body.appendChild(this.element);
  }

  show() {
    this.element.classList.remove('hidden');
    this.visible = true;
  }

  hide() {
    this.element.classList.add('hidden');
    this.visible = false;
  }

  toggle() {
    if (this.visible) {
      this.hide();
    } else {
      this.show();
    }
  }
}

window.DanmakuLayer = DanmakuLayer;
