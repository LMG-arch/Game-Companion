// frontend/renderer/index.js
/**
 * 前端入口 JS
 * 初始化 WebSocket 连接，处理消息
 */

const { ipcRenderer } = require('electron');

const statusEl = document.getElementById('status');
const testResultEl = document.getElementById('test-result');

// 更新连接状态显示
function updateStatus(connected) {
  if (connected) {
    statusEl.textContent = '✅ 已连接';
    statusEl.className = 'connected';
  } else {
    statusEl.textContent = '❌ 已断开';
    statusEl.className = 'disconnected';
  }
}

// 监听 Python 就绪事件
ipcRenderer.on('python-ready', (event, { port }) => {
  console.log(`Python 端口: ${port}`);
  wsClient.connect(port);
});

// WebSocket 事件监听
wsClient.on('connected', () => {
  updateStatus(true);
  testResultEl.textContent = '已连接到后端';
});

wsClient.on('disconnected', () => {
  updateStatus(false);
});

// 收到 pong
wsClient.on('pong', (payload) => {
  testResultEl.textContent = `收到 Pong: ${JSON.stringify(payload)}`;
});

// 收到问题回答
wsClient.on('question.answer.result', (payload) => {
  testResultEl.textContent = `回答: ${JSON.stringify(payload)}`;
});

// 收到错误
wsClient.on('error', (payload) => {
  testResultEl.textContent = `错误: ${payload.message}`;
});

// 测试按钮
document.getElementById('btn-ping').addEventListener('click', () => {
  const id = wsClient.send('ping');
  testResultEl.textContent = `已发送 Ping (id: ${id})`;
});

document.getElementById('btn-question').addEventListener('click', () => {
  const id = wsClient.send('question.ask', { text: '测试问题' });
  testResultEl.textContent = `已发送提问 (id: ${id})`;
});

// 点击穿透控制：鼠标进入可交互元素时禁用穿透，离开时恢复
document.querySelectorAll('button, input, .interactive').forEach(el => {
  el.addEventListener('mouseenter', () => {
    ipcRenderer.send('set-ignore-mouse-events', false);
  });
  el.addEventListener('mouseleave', () => {
    ipcRenderer.send('set-ignore-mouse-events', true, { forward: true });
  });
});

// 测试区域整体可交互
const testArea = document.getElementById('test-area');
if (testArea) {
  testArea.addEventListener('mouseenter', () => {
    ipcRenderer.send('set-ignore-mouse-events', false);
  });
  testArea.addEventListener('mouseleave', () => {
    ipcRenderer.send('set-ignore-mouse-events', true, { forward: true });
  });
}

console.log('前端已加载');
