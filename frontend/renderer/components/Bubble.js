// frontend/renderer/components/Bubble.js
/**
 * 浮动气泡组件
 * 显示 AI 状态、快捷操作
 */

class Bubble {
  constructor() {
    this.element = null;
    this.visible = true;
    this.aiStatus = 'offline';
    this.init();
  }

  init() {
    this.element = document.createElement('div');
    this.element.id = 'bubble';
    this.element.style.cssText = `
      position: fixed;
      bottom: 20px;
      left: 20px;
      width: 80px;
      height: 80px;
      z-index: 40;
      cursor: pointer;
      transition: transform 0.2s ease;
    `;

    this.element.innerHTML = `
      <div id="bubble-inner" style="
        width: 100%;
        height: 100%;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        background: rgba(0, 0, 0, 0.85);
        border-radius: 50%;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.5);
        backdrop-filter: blur(10px);
        border: 2px solid rgba(255, 255, 255, 0.2);
        transition: border-color 0.3s ease;
      ">
        <span style="font-size: 28px;">🤖</span>
        <span id="bubble-status" style="font-size: 9px; color: #f44336; margin-top: 2px;">离线</span>
      </div>
      <div id="bubble-tooltip" style="
        display: none;
        position: absolute;
        bottom: 90px;
        left: 0;
        background: rgba(0, 0, 0, 0.95);
        border-radius: 8px;
        padding: 10px 14px;
        min-width: 150px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.5);
        border: 1px solid rgba(255, 255, 255, 0.2);
        pointer-events: none;
      ">
        <p id="tooltip-status" style="font-size: 12px; color: #f44336; margin: 0 0 6px 0;">AI 状态：离线</p>
        <p id="tooltip-info" style="font-size: 11px; color: rgba(255,255,255,0.6); margin: 0;">等待连接...</p>
      </div>
    `;

    document.body.appendChild(this.element);

    // 注册到点击穿透模块
    if (window.clickThrough) {
      window.clickThrough.register(this.element);
    }

    // 鼠标悬停显示详情
    this.element.addEventListener('mouseenter', () => {
      this.element.style.transform = 'scale(1.1)';
      this.element.querySelector('#bubble-tooltip').style.display = 'block';
    });

    this.element.addEventListener('mouseleave', () => {
      this.element.style.transform = 'scale(1)';
      this.element.querySelector('#bubble-tooltip').style.display = 'none';
    });

    // 点击打开设置
    this.element.addEventListener('click', () => {
      window.dispatchEvent(new CustomEvent('open-settings'));
    });
  }

  setAIStatus(status, info = '') {
    this.aiStatus = status;
    const inner = this.element.querySelector('#bubble-inner');
    const statusEl = this.element.querySelector('#bubble-status');
    const tooltipStatus = this.element.querySelector('#tooltip-status');
    const tooltipInfo = this.element.querySelector('#tooltip-info');

    const statusMap = {
      'online': { text: '在线', color: '#4caf50', border: 'rgba(76, 175, 80, 0.5)' },
      'offline': { text: '离线', color: '#f44336', border: 'rgba(244, 67, 54, 0.5)' },
      'error': { text: '错误', color: '#ff9800', border: 'rgba(255, 152, 0, 0.5)' },
    };

    const s = statusMap[status] || statusMap['offline'];
    statusEl.textContent = s.text;
    statusEl.style.color = s.color;
    inner.style.borderColor = s.border;
    tooltipStatus.textContent = `AI 状态：${s.text}`;
    tooltipStatus.style.color = s.color;
    tooltipInfo.textContent = info || this._getDefaultInfo(status);
  }

  _getDefaultInfo(status) {
    switch (status) {
      case 'online': return '正常工作中';
      case 'offline': return '未配置 API Key';
      case 'error': return 'API 调用失败';
      default: return '';
    }
  }

  show() {
    this.element.style.display = 'block';
    this.visible = true;
  }

  hide() {
    this.element.style.display = 'none';
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

window.Bubble = Bubble;
