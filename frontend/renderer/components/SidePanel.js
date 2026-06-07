// frontend/renderer/components/SidePanel.js
/**
 * 右侧侧边栏组件
 * 显示问答结果、AI 分析、记忆信息
 */

class SidePanel {
  constructor() {
    this.element = null;
    this.visible = true;
    this.init();
  }

  init() {
    this.element = document.createElement('div');
    this.element.id = 'side-panel';
    this.element.className = 'module';
    this.element.style.cssText = `
      position: fixed;
      top: 50px;
      right: 0;
      width: 300px;
      max-height: calc(100vh - 60px);
      background: rgba(0, 0, 0, 0.85);
      border-radius: 8px 0 0 8px;
      padding: 12px;
      z-index: 50;
      overflow-y: auto;
      backdrop-filter: blur(10px);
      pointer-events: none;
      transition: transform 0.3s ease;
    `;

    this.element.innerHTML = `
      <div style="margin-bottom: 12px;">
        <h3 style="font-size: 14px; color: rgba(255,255,255,0.8); margin-bottom: 8px;">💬 问答结果</h3>
        <div id="side-content" style="font-size: 13px; line-height: 1.6; color: rgba(255,255,255,0.9);">
          暂无内容
        </div>
      </div>
      <div style="margin-top: 12px; padding-top: 12px; border-top: 1px solid rgba(255,255,255,0.1);">
        <h3 style="font-size: 14px; color: rgba(255,255,255,0.8); margin-bottom: 8px;">🎮 游戏状态</h3>
        <div id="game-status" style="font-size: 12px; color: rgba(255,255,255,0.6);">
          等待分析...
        </div>
      </div>
    `;

    document.body.appendChild(this.element);

    // 鼠标悬停时可交互
    this.element.addEventListener('mouseenter', () => {
      this.element.style.pointerEvents = 'auto';
      if (window.ipcRenderer) {
        window.ipcRenderer.send('set-ignore-mouse-events', false);
      }
    });

    this.element.addEventListener('mouseleave', () => {
      this.element.style.pointerEvents = 'none';
      if (window.ipcRenderer) {
        window.ipcRenderer.send('set-ignore-mouse-events', true, { forward: true });
      }
    });
  }

  setContent(html) {
    const contentEl = this.element.querySelector('#side-content');
    if (contentEl) {
      contentEl.innerHTML = html;
    }
  }

  setGameStatus(text) {
    const statusEl = this.element.querySelector('#game-status');
    if (statusEl) {
      statusEl.textContent = text;
    }
  }

  show() {
    this.element.classList.remove('hidden');
    this.element.style.transform = 'translateX(0)';
    this.visible = true;
  }

  hide() {
    this.element.style.transform = 'translateX(100%)';
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

// 导出
window.SidePanel = SidePanel;
