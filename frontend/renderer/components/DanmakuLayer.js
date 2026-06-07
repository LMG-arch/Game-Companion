// frontend/renderer/components/DanmakuLayer.js
/**
 * 弹幕层组件
 * 管理弹幕显示和动画
 */

class DanmakuLayer {
  constructor() {
    this.element = null;
    this.visible = true;
    this.tracks = [[], [], []]; // 上/中/下三轨道
    this.queue = []; // 待显示队列
    this.maxPerSecond = 5;
    this.lastSendTime = 0;
    this.init();
  }

  init() {
    this.element = document.createElement('div');
    this.element.id = 'danmaku-layer';
    this.element.className = 'module';
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

  /**
   * 发送弹幕
   * @param {string} text - 弹幕文本
   * @param {string} priority - 优先级: high/normal/low
   * @param {string} style - 样式: encouragement/tutorial/comment
   */
  send(text, priority = 'normal', style = 'encouragement') {
    const now = Date.now();
    const timeSinceLastSend = now - this.lastSendTime;

    // 密度控制
    if (timeSinceLastSend < 1000 / this.maxPerSecond) {
      if (priority !== 'high') {
        // 低优先级弹幕排队
        if (this.queue.length < 50) {
          this.queue.push({ text, priority, style });
        }
        return;
      }
    }

    this.lastSendTime = now;
    this._render(text, style);
  }

  _render(text, style) {
    // 选择轨道（负载最少的）
    const trackIndex = this._selectTrack();
    const trackY = 50 + trackIndex * 60; // 轨道 Y 坐标

    // 创建弹幕元素
    const el = document.createElement('div');
    el.className = 'danmaku-item';
    el.style.cssText = `
      position: absolute;
      right: -300px;
      top: ${trackY}px;
      white-space: nowrap;
      font-size: 16px;
      color: white;
      text-shadow: 1px 1px 2px rgba(0,0,0,0.8);
      animation: danmaku-scroll 8s linear forwards;
      pointer-events: none;
    `;

    // 样式
    if (style === 'encouragement') {
      el.style.color = '#4caf50';
    } else if (style === 'tutorial') {
      el.style.color = '#2196f3';
    }

    el.textContent = text;
    this.element.appendChild(el);

    // 轨道管理
    this.tracks[trackIndex].push(el);

    // 动画结束后移除
    el.addEventListener('animationend', () => {
      el.remove();
      const idx = this.tracks[trackIndex].indexOf(el);
      if (idx > -1) {
        this.tracks[trackIndex].splice(idx, 1);
      }
      // 处理队列
      if (this.queue.length > 0) {
        const next = this.queue.shift();
        this.send(next.text, next.priority, next.style);
      }
    });
  }

  _selectTrack() {
    // 选择负载最少的轨道
    let minLen = Infinity;
    let minIdx = 0;
    for (let i = 0; i < this.tracks.length; i++) {
      if (this.tracks[i].length < minLen) {
        minLen = this.tracks[i].length;
        minIdx = i;
      }
    }
    return minIdx;
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

// 导出
window.DanmakuLayer = DanmakuLayer;
