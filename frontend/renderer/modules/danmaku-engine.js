// frontend/renderer/modules/danmaku-engine.js
/**
 * 弹幕引擎模块
 * 队列管理、轨道系统、密度控制、优先级队列
 */

class DanmakuEngine {
  constructor() {
    this.tracks = [[], [], []]; // 上/中/下三轨道
    this.queue = []; // 待显示队列
    this.maxQueueSize = 50;
    this.maxPerSecond = 5;
    this.lastSendTime = 0;
    this.layer = null;
    this.history = []; // 弹幕历史
    this.maxHistory = 1000;
  }

  /**
   * 初始化
   * @param {DanmakuLayer} layer - 弹幕层组件
   */
  init(layer) {
    this.layer = layer;
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
        this._enqueue(text, priority, style);
        return;
      }
    }

    this.lastSendTime = now;
    this._render(text, priority, style);
  }

  /**
   * 批量发送弹幕
   * @param {Array} danmakus - [{text, priority, style}]
   */
  sendBatch(danmakus) {
    for (const d of danmakus) {
      this.send(d.text, d.priority, d.style);
    }
  }

  /**
   * 入队
   */
  _enqueue(text, priority, style) {
    // 队列满时丢弃低优先级
    if (this.queue.length >= this.maxQueueSize) {
      const lowIdx = this.queue.findIndex(d => d.priority === 'low');
      if (lowIdx >= 0) {
        this.queue.splice(lowIdx, 1);
      } else {
        this.queue.shift(); // 丢弃最早的
      }
    }

    // 高优先级插队
    if (priority === 'high') {
      this.queue.unshift({ text, priority, style });
    } else {
      this.queue.push({ text, priority, style });
    }
  }

  /**
   * 渲染弹幕
   */
  _render(text, priority, style) {
    if (!this.layer) return;

    // 选择轨道
    const trackIndex = this._selectTrack();
    const trackY = 50 + trackIndex * 60;

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
    } else if (style === 'comment') {
      el.style.color = '#ff9800';
    }

    // 优先级样式
    if (priority === 'high') {
      el.style.fontSize = '18px';
      el.style.fontWeight = 'bold';
    }

    el.textContent = text;
    this.layer.element.appendChild(el);

    // 轨道管理
    this.tracks[trackIndex].push(el);

    // 记录历史
    this._addHistory(text, priority, style);

    // 动画结束后移除
    el.addEventListener('animationend', () => {
      el.remove();
      const idx = this.tracks[trackIndex].indexOf(el);
      if (idx > -1) {
        this.tracks[trackIndex].splice(idx, 1);
      }
      // 处理队列
      this._processQueue();
    });
  }

  /**
   * 处理队列
   */
  _processQueue() {
    if (this.queue.length === 0) return;

    const now = Date.now();
    const timeSinceLastSend = now - this.lastSendTime;

    if (timeSinceLastSend >= 1000 / this.maxPerSecond) {
      const next = this.queue.shift();
      this.send(next.text, next.priority, next.style);
    }
  }

  /**
   * 选择轨道（负载最少的）
   */
  _selectTrack() {
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

  /**
   * 添加到历史
   */
  _addHistory(text, priority, style) {
    this.history.push({
      text,
      priority,
      style,
      time: Date.now(),
    });

    // 限制历史大小
    if (this.history.length > this.maxHistory) {
      this.history.shift();
    }
  }

  /**
   * 获取历史
   */
  getHistory(limit = 50) {
    return this.history.slice(-limit);
  }

  /**
   * 清空队列
   */
  clearQueue() {
    this.queue = [];
  }

  /**
   * 设置密度
   * @param {number} maxPerSecond - 每秒最大弹幕数
   */
  setDensity(maxPerSecond) {
    this.maxPerSecond = Math.max(1, Math.min(20, maxPerSecond));
  }
}

// 导出单例
window.danmakuEngine = new DanmakuEngine();
