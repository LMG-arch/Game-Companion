// frontend/renderer/modules/web-socket.js
/**
 * WebSocket 客户端模块
 * 负责连接、重连、消息收发
 */

class WebSocketClient {
  constructor() {
    this.ws = null;
    this.url = null;
    this.handlers = {};
    this.reconnectTimer = null;
    this.reconnectDelay = 3000; // 初始重连延迟 3 秒
    this.maxReconnectDelay = 30000; // 最大重连延迟 30 秒
    this.isConnected = false;
  }

  /**
   * 连接到 WebSocket 服务器
   * @param {number} port - 端口号
   */
  connect(port) {
    this.url = `ws://localhost:${port}`;
    console.log(`正在连接 WebSocket: ${this.url}`);

    this.ws = new WebSocket(this.url);

    this.ws.onopen = () => {
      console.log('WebSocket 已连接');
      this.isConnected = true;
      this.reconnectDelay = 3000; // 重置重连延迟
      this._emit('connected', {});
    };

    this.ws.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data);
        console.log(`收到消息: ${message.type}`);
        this._emit(message.type, message.payload || {});
        this._emit('message', message);
      } catch (e) {
        console.error('解析消息失败:', e);
      }
    };

    this.ws.onclose = () => {
      console.log('WebSocket 已断开');
      this.isConnected = false;
      this._emit('disconnected', {});
      this._scheduleReconnect();
    };

    this.ws.onerror = (error) => {
      console.error('WebSocket 错误:', error);
    };
  }

  /**
   * 发送消息
   * @param {string} type - 消息类型
   * @param {object} payload - 消息内容
   * @returns {string} 消息 ID
   */
  send(type, payload = {}) {
    if (!this.isConnected) {
      console.warn('WebSocket 未连接，无法发送消息');
      return null;
    }

    const id = crypto.randomUUID();
    const message = { type, id, payload };
    this.ws.send(JSON.stringify(message));
    return id;
  }

  /**
   * 注册消息处理器
   * @param {string} type - 消息类型
   * @param {function} handler - 处理函数
   */
  on(type, handler) {
    if (!this.handlers[type]) {
      this.handlers[type] = [];
    }
    this.handlers[type].push(handler);
  }

  /**
   * 触发事件
   */
  _emit(type, data) {
    const handlers = this.handlers[type] || [];
    handlers.forEach(handler => {
      try {
        handler(data);
      } catch (e) {
        console.error(`处理器 ${type} 出错:`, e);
      }
    });
  }

  /**
   * 计划重连
   */
  _scheduleReconnect() {
    if (this.reconnectTimer) return;

    console.log(`${this.reconnectDelay / 1000} 秒后重连...`);
    this.reconnectTimer = setTimeout(() => {
      this.reconnectTimer = null;
      if (this.url) {
        this.connect(this.url.replace('ws://localhost:', ''));
      }
    }, this.reconnectDelay);

    // 指数退避
    this.reconnectDelay = Math.min(this.reconnectDelay * 2, this.maxReconnectDelay);
  }

  /**
   * 断开连接
   */
  disconnect() {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    this.isConnected = false;
  }
}

// 导出单例
window.wsClient = new WebSocketClient();
