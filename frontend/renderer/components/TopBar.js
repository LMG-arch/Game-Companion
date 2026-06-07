// frontend/renderer/components/TopBar.js
/**
 * 顶部工具栏组件
 * 显示状态信息、快捷操作按钮
 */

class TopBar {
  constructor() {
    this.element = null;
    this.visible = true;
    this.init();
  }

  init() {
    this.element = document.createElement('div');
    this.element.id = 'top-bar';
    this.element.style.cssText = `
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      height: 40px;
      background: rgba(0, 0, 0, 0.8);
      display: flex;
      align-items: center;
      padding: 0 12px;
      z-index: 30;
      backdrop-filter: blur(10px);
    `;

    this.element.innerHTML = `
      <div style="display: flex; align-items: center; gap: 12px; width: 100%;">
        <span id="topbar-status" style="font-size: 12px; color: #4caf50;">● 就绪</span>
        <span id="topbar-fps" style="font-size: 12px; color: rgba(255,255,255,0.6);">FPS: --</span>
        <div style="flex: 1;"></div>
        <button class="btn" id="btn-search" style="padding: 4px 12px; font-size: 12px;">🔍 搜索</button>
        <button class="btn" id="btn-settings" style="padding: 4px 12px; font-size: 12px;">⚙️ 设置</button>
      </div>
    `;

    document.body.appendChild(this.element);

    // 鼠标悬停时禁用穿透
    this.element.addEventListener('mouseenter', () => {
      if (window.clickThrough) {
        window.clickThrough.disable();
      }
    });

    this.element.addEventListener('mouseleave', () => {
      // 延迟恢复穿透，避免点击按钮时立即穿透
      setTimeout(() => {
        if (window.clickThrough && !this._isOverButton) {
          window.clickThrough.enable();
        }
      }, 100);
    });

    // 按钮悬停标记
    this.element.querySelectorAll('button').forEach(btn => {
      btn.addEventListener('mouseenter', () => {
        this._isOverButton = true;
      });
      btn.addEventListener('mouseleave', () => {
        this._isOverButton = false;
      });
    });
  }

  setStatus(text, color = '#4caf50') {
    const statusEl = this.element.querySelector('#topbar-status');
    if (statusEl) {
      statusEl.textContent = `● ${text}`;
      statusEl.style.color = color;
    }
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

window.TopBar = TopBar;
