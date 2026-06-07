// frontend/renderer/index.js
/**
 * 前端入口 JS
 * 初始化所有 UI 组件，处理 WebSocket 消息
 */

// HTML 转义函数，防止 XSS
function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

// 全局组件实例
let topBar, sidePanel, bubble, danmakuLayer, chatInput, personalityEditor, settingsPanel;

// 初始化组件
function initComponents() {
  topBar = new TopBar();
  sidePanel = new SidePanel();
  bubble = new Bubble();
  danmakuLayer = new DanmakuLayer();
  chatInput = new ChatInput();
  personalityEditor = new PersonalityEditor();
  settingsPanel = new SettingsPanel();

  // 初始化弹幕引擎
  danmakuEngine.init(danmakuLayer);

  // 初始化点击穿透
  clickThrough.init();

  // 输入框提交回调
  chatInput.onSubmit = (text) => {
    const id = wsClient.send('question.ask', { text });
    console.log(`已发送提问: ${text}`);
    sidePanel.setContent(`<p>正在搜索: ${escapeHtml(text)}...</p>`);
  };

  // 设置面板按钮（打开设置面板）
  const settingsBtn = document.getElementById('btn-settings');
  if (settingsBtn) {
    settingsBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      settingsPanel.toggle();
    });
  }

  // 搜索按钮
  const searchBtn = document.getElementById('btn-search');
  if (searchBtn) {
    searchBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      chatInput.toggle();
    });
  }

  console.log('UI 组件已初始化');
}

// 监听 Python 就绪事件
if (window.electronAPI) {
  window.electronAPI.on('python-ready', ({ port }) => {
    console.log(`Python 端口: ${port}`);
    wsClient.connect(port);
  });

  // 监听主进程快捷键消息
  window.electronAPI.on('shortcut', (action) => {
    switch (action) {
      case 'toggle-input':
        chatInput.toggle();
        break;
      case 'toggle-ui':
        topBar.toggle();
        sidePanel.toggle();
        bubble.toggle();
        break;
      case 'open-settings':
        settingsPanel.toggle();
        break;
      case 'toggle-danmaku':
        danmakuLayer.toggle();
        break;
    }
  });
}

// WebSocket 事件监听
wsClient.on('connected', () => {
  topBar.setStatus('已连接', '#4caf50');
  sidePanel.setContent('<p style="color: #4caf50;">✅ 已连接到后端</p>');
  bubble.setAIStatus('online', '已连接后端');
});

wsClient.on('disconnected', () => {
  topBar.setStatus('已断开', '#f44336');
  sidePanel.setContent('<p style="color: #f44336;">❌ 连接断开，正在重连...</p>');
  bubble.setAIStatus('offline', '连接断开');
});

// AI 状态变化
wsClient.on('ai.status', (payload) => {
  const { status, message } = payload;
  bubble.setAIStatus(status, message);
});

// 收到场景分析结果
wsClient.on('screen.analyzed', (payload) => {
  const { scene, description, suggestion, danmaku_hint } = payload;
  sidePanel.setGameStatus(`场景: ${scene}`);
  if (danmaku_hint) {
    danmakuEngine.send(danmaku_hint, 'normal', 'encouragement');
  }
});

// 收到弹幕
wsClient.on('danmaku.send', (payload) => {
  const { text, priority, style } = payload;
  danmakuEngine.send(text, priority, style);
});

// 收到问题回答
wsClient.on('question.answer.result', (payload) => {
  const { answer, sources } = payload;
  const safeAnswer = escapeHtml(answer || '');
  let html = `<p>${safeAnswer}</p>`;
  if (sources && sources.length > 0) {
    html += '<div style="margin-top: 8px; font-size: 11px; color: rgba(255,255,255,0.6);">';
    sources.forEach(s => {
      const safeTitle = escapeHtml(s.title || '');
      const safeUrl = escapeHtml(s.url || '');
      html += `<p>📎 <a href="${safeUrl}" style="color: #64b5f6;">${safeTitle}</a></p>`;
    });
    html += '</div>';
  }
  sidePanel.setContent(html);
});

// 收到错误
wsClient.on('error', (payload) => {
  console.error('错误:', payload);
  sidePanel.setContent(`<p style="color: #f44336;">错误: ${escapeHtml(payload.message)}</p>`);
});

// 收到人格列表
wsClient.on('personality.list.result', (payload) => {
  const { list, active_id } = payload;
  personalityEditor.setPersonalities(list, active_id);
});

// 收到人格切换结果
wsClient.on('personality.switch.result', (payload) => {
  const { success, active_id } = payload;
  if (success) {
    sidePanel.setContent('<p style="color: #4caf50;">✅ 人格已切换</p>');
    personalityEditor.loadPersonalities();
  }
});

// 收到人格生成结果
wsClient.on('personality.generate.result', (payload) => {
  const { success, personality, error } = payload;
  if (success) {
    sidePanel.setContent(`<p style="color: #4caf50;">✅ 人格已生成: ${escapeHtml(personality.name)}</p>`);
    personalityEditor.loadPersonalities();
  } else {
    sidePanel.setContent(`<p style="color: #f44336;">❌ 生成失败: ${escapeHtml(error)}</p>`);
  }
});

// 收到配置
wsClient.on('settings.get.result', (payload) => {
  settingsPanel.setConfig(payload);
});

// 收到配置保存结果
wsClient.on('settings.save.result', (payload) => {
  if (payload.success) {
    sidePanel.setContent('<p style="color: #4caf50;">✅ 配置已保存</p>');
  }
});

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', () => {
  initComponents();

  // 监听气泡点击打开设置事件
  window.addEventListener('open-settings', () => {
    if (settingsPanel) settingsPanel.toggle();
  });
});

console.log('前端已加载');
