// frontend/renderer/components/Bubble.js
/**
 * 浮动气泡组件
 * 显示鼓励语、快捷操作
 */

class Bubble {
  constructor() {
    this.element = null;
    this.visible = true;
    this.messages = [
      '加油！你可以的！',
      '太棒了！',
      '继续努力！',
      '相信自己！'
    ];
    this.init();
  }

  init() {
    this.element = document.createElement('div');
    this.element.id = 'bubble';
    this.element.className = 'module';
    this.element.style.cssText = `
      position: fixed;
      bottom: 20px;
      left: 20px;
      width: 120px;
      height: 120px;
      z-index: 40;
      pointer-events: none;
      transition: transform 0.3s ease, opacity 0.3s ease;
      cursor: pointer;
    `;

    this.element.innerHTML = `
      <div style="
        width: 100%;
        height: 100%;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        background: rgba(0, 0, 0, 0.8);
        border-radius: 50%;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.5);
        backdrop-filter: blur(10px);
        border: 2px solid rgba(255, 255, 255, 0.2);
      ">
        <span style="font-size: 32px; margin-bottom: 4px;">🤖</span>
        <span id="bubble-text" style="font-size: 11px; text-align: center; padding: 0 8px; color: rgba(255,255,255,0.9);">加油！</span>
      </div>
    `;

    document.body.appendChild(this.element);

    // 鼠标悬停时可交互
    this.element.addEventListener('mouseenter', () => {
      this.element.style.pointerEvents = 'auto';
      this.element.style.transform = 'scale(1.1)';
      if (window.ipcRenderer) {
        window.ipcRenderer.send('set-ignore-mouse-events', false);
      }
    });

    this.element.addEventListener('mouseleave', () => {
      this.element.style.pointerEvents = 'none';
      this.element.style.transform = 'scale(1)';
      if (window.ipcRenderer) {
        window.ipcRenderer.send('set-ignore-mouse-events', true, { forward: true });
      }
    });

    // 点击切换消息
    this.element.addEventListener('click', () => {
      this.randomMessage();
    });

    // 定时切换消息
    setInterval(() => this.randomMessage(), 10000);
  }

  randomMessage() {
    const textEl = this.element.querySelector('#bubble-text');
    if (textEl) {
      const msg = this.messages[Math.floor(Math.random() * this.messages.length)];
      textEl.textContent = msg;
    }
  }

  setMessage(text) {
    const textEl = this.element.querySelector('#bubble-text');
    if (textEl) {
      textEl.textContent = text;
    }
  }

  show() {
    this.element.classList.remove('hidden');
    this.element.style.opacity = '1';
    this.visible = true;
  }

  hide() {
    this.element.style.opacity = '0';
    setTimeout(() => {
      this.element.classList.add('hidden');
    }, 300);
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
window.Bubble = Bubble;
