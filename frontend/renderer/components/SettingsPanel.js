// frontend/renderer/components/SettingsPanel.js
/**
 * 设置面板组件
 * 完整配置面板 + 配置持久化
 */

class SettingsPanel {
  constructor() {
    this.element = null;
    this.visible = false;
    this.activeTab = 'general';
    this.config = {};
    this.init();
  }

  init() {
    this.element = document.createElement('div');
    this.element.id = 'settings-panel';
    this.element.className = 'hidden';
    this.element.style.cssText = `
      position: fixed;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
      width: 600px;
      max-height: 85vh;
      background: rgba(0, 0, 0, 0.95);
      border-radius: 12px;
      padding: 0;
      z-index: 100;
      overflow: hidden;
      backdrop-filter: blur(10px);
      border: 1px solid rgba(255, 255, 255, 0.2);
      pointer-events: auto;
      display: flex;
      flex-direction: column;
    `;

    this.element.innerHTML = `
      <!-- 标题栏 -->
      <div style="display: flex; justify-content: space-between; align-items: center; padding: 16px 20px; border-bottom: 1px solid rgba(255,255,255,0.1);">
        <h2 style="font-size: 18px; color: #fff; margin: 0;">⚙️ 设置</h2>
        <button id="close-settings" style="background: none; border: none; color: #fff; font-size: 20px; cursor: pointer;">✕</button>
      </div>

      <!-- 标签页 -->
      <div id="settings-tabs" style="display: flex; padding: 0 20px; border-bottom: 1px solid rgba(255,255,255,0.1); overflow-x: auto;">
        <button class="settings-tab active" data-tab="general">通用</button>
        <button class="settings-tab" data-tab="ui">界面</button>
        <button class="settings-tab" data-tab="ai">AI</button>
        <button class="settings-tab" data-tab="game">游戏</button>
        <button class="settings-tab" data-tab="danmaku">弹幕</button>
        <button class="settings-tab" data-tab="search">搜索</button>
        <button class="settings-tab" data-tab="memory">记忆</button>
      </div>

      <!-- 内容区 -->
      <div id="settings-content" style="flex: 1; overflow-y: auto; padding: 20px;">
        <!-- 动态生成 -->
      </div>

      <!-- 底部按钮 -->
      <div style="display: flex; justify-content: flex-end; gap: 8px; padding: 16px 20px; border-top: 1px solid rgba(255,255,255,0.1);">
        <button id="settings-export" class="btn" style="padding: 8px 16px; font-size: 13px; background: rgba(255,255,255,0.1);">导出配置</button>
        <button id="settings-import" class="btn" style="padding: 8px 16px; font-size: 13px; background: rgba(255,255,255,0.1);">导入配置</button>
        <button id="settings-save" class="btn" style="padding: 8px 16px; font-size: 13px;">保存</button>
      </div>
    `;

    document.body.appendChild(this.element);

    // 添加样式
    const style = document.createElement('style');
    style.textContent = `
      .settings-tab {
        padding: 10px 16px;
        background: none;
        border: none;
        color: rgba(255,255,255,0.6);
        cursor: pointer;
        font-size: 13px;
        border-bottom: 2px solid transparent;
        white-space: nowrap;
      }
      .settings-tab:hover {
        color: rgba(255,255,255,0.8);
      }
      .settings-tab.active {
        color: #2196f3;
        border-bottom-color: #2196f3;
      }
      .settings-group {
        margin-bottom: 20px;
      }
      .settings-group h3 {
        font-size: 14px;
        color: rgba(255,255,255,0.8);
        margin-bottom: 12px;
        padding-bottom: 8px;
        border-bottom: 1px solid rgba(255,255,255,0.1);
      }
      .settings-item {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 12px;
      }
      .settings-item label {
        font-size: 13px;
        color: rgba(255,255,255,0.8);
      }
      .settings-item input[type="text"],
      .settings-item input[type="number"],
      .settings-item select,
      .settings-item textarea {
        background: rgba(255,255,255,0.1);
        border: 1px solid rgba(255,255,255,0.2);
        border-radius: 6px;
        padding: 6px 10px;
        color: white;
        font-size: 13px;
        outline: none;
        width: 200px;
      }
      .settings-item textarea {
        width: 100%;
        height: 80px;
        resize: vertical;
      }
      .settings-item input[type="range"] {
        width: 150px;
      }
      .settings-item input[type="checkbox"] {
        width: 18px;
        height: 18px;
        cursor: pointer;
      }
    `;
    document.head.appendChild(style);

    // 事件绑定
    this.element.querySelector('#close-settings').addEventListener('click', () => this.hide());

    // 标签切换
    this.element.querySelectorAll('.settings-tab').forEach(tab => {
      tab.addEventListener('click', () => {
        this.activeTab = tab.dataset.tab;
        this._updateTabs();
        this._renderContent();
      });
    });

    // 保存按钮
    this.element.querySelector('#settings-save').addEventListener('click', () => this._save());

    // 导出按钮
    this.element.querySelector('#settings-export').addEventListener('click', () => this._export());

    // 导入按钮
    this.element.querySelector('#settings-import').addEventListener('click', () => this._import());
  }

  async loadConfig() {
    // 从后端加载配置
    if (window.wsClient && window.wsClient.isConnected) {
      window.wsClient.send('settings.get');
    }
  }

  setConfig(config) {
    this.config = config;
    this._renderContent();
  }

  _updateTabs() {
    this.element.querySelectorAll('.settings-tab').forEach(tab => {
      tab.classList.toggle('active', tab.dataset.tab === this.activeTab);
    });
  }

  _renderContent() {
    const content = this.element.querySelector('#settings-content');
    if (!content) return;

    const renderers = {
      general: () => this._renderGeneral(),
      ui: () => this._renderUI(),
      ai: () => this._renderAI(),
      game: () => this._renderGame(),
      danmaku: () => this._renderDanmaku(),
      search: () => this._renderSearch(),
      memory: () => this._renderMemory(),
    };

    content.innerHTML = (renderers[this.activeTab] || renderers.general)();
  }

  _renderGeneral() {
    const c = this.config.general || {};
    return `
      <div class="settings-group">
        <h3>通用设置</h3>
        <div class="settings-item">
          <label>开机自启</label>
          <input type="checkbox" id="s-auto-launch" ${c.auto_launch ? 'checked' : ''}>
        </div>
        <div class="settings-item">
          <label>语言</label>
          <select id="s-language">
            <option value="zh-CN" ${c.language === 'zh-CN' ? 'selected' : ''}>中文</option>
            <option value="en" ${c.language === 'en' ? 'selected' : ''}>English</option>
          </select>
        </div>
      </div>
      <div class="settings-group">
        <h3>模块开关</h3>
        <div class="settings-item">
          <label>顶部工具栏</label>
          <input type="checkbox" id="s-mod-toolbar" ${c.modules?.toolbar ? 'checked' : ''}>
        </div>
        <div class="settings-item">
          <label>右侧侧边栏</label>
          <input type="checkbox" id="s-mod-sidebar" ${c.modules?.sidebar ? 'checked' : ''}>
        </div>
        <div class="settings-item">
          <label>浮动气泡</label>
          <input type="checkbox" id="s-mod-bubble" ${c.modules?.bubble ? 'checked' : ''}>
        </div>
        <div class="settings-item">
          <label>弹幕层</label>
          <input type="checkbox" id="s-mod-danmaku" ${c.modules?.danmaku ? 'checked' : ''}>
        </div>
      </div>
    `;
  }

  _renderUI() {
    const c = this.config.ui || {};
    return `
      <div class="settings-group">
        <h3>界面设置</h3>
        <div class="settings-item">
          <label>透明度: ${c.opacity || 90}%</label>
          <input type="range" id="s-opacity" min="0" max="100" value="${c.opacity || 90}">
        </div>
        <div class="settings-item">
          <label>主题</label>
          <select id="s-theme">
            <option value="dark" ${c.theme === 'dark' ? 'selected' : ''}>深色</option>
            <option value="light" ${c.theme === 'light' ? 'selected' : ''}>浅色</option>
          </select>
        </div>
      </div>
      <div class="settings-group">
        <h3>弹幕样式</h3>
        <div class="settings-item">
          <label>字体大小</label>
          <input type="number" id="s-danmaku-size" value="${c.danmaku?.font_size || 16}" min="12" max="24">
        </div>
        <div class="settings-item">
          <label>字体颜色</label>
          <input type="text" id="s-danmaku-color" value="${c.danmaku?.color || '#FFFFFF'}">
        </div>
      </div>
    `;
  }

  _renderAI() {
    const c = this.config.ai || {};
    return `
      <div class="settings-group">
        <h3>AI 设置</h3>
        <div class="settings-item">
          <label>Provider</label>
          <select id="s-ai-provider">
            <option value="openai" ${c.provider === 'openai' ? 'selected' : ''}>OpenAI</option>
            <option value="claude" ${c.provider === 'claude' ? 'selected' : ''}>Claude</option>
            <option value="custom" ${c.provider === 'custom' ? 'selected' : ''}>自定义</option>
          </select>
        </div>
        <div class="settings-item">
          <label>API 地址</label>
          <input type="text" id="s-ai-url" value="${c.api_url || ''}">
        </div>
        <div class="settings-item">
          <label>API Key</label>
          <input type="text" id="s-ai-key" value="${c.api_key || ''}" placeholder="sk-xxx">
        </div>
        <div class="settings-item">
          <label>模型</label>
          <input type="text" id="s-ai-model" value="${c.model || ''}">
        </div>
        <div class="settings-item">
          <label>Temperature</label>
          <input type="number" id="s-ai-temp" value="${c.temperature || 0.7}" min="0" max="2" step="0.1">
        </div>
        <div class="settings-item">
          <label>系统提示词</label>
          <textarea id="s-ai-prompt">${c.system_prompt || ''}</textarea>
        </div>
      </div>
    `;
  }

  _renderGame() {
    const c = this.config.game || {};
    return `
      <div class="settings-group">
        <h3>游戏设置</h3>
        <div class="settings-item">
          <label>截图频率 (FPS)</label>
          <input type="number" id="s-capture-fps" value="${c.capture_fps || 1}" min="0.1" max="5" step="0.1">
        </div>
        <div class="settings-item">
          <label>静默帧率</label>
          <input type="number" id="s-silent-fps" value="${c.silent_fps || 0.2}" min="0.05" max="1" step="0.05">
        </div>
        <div class="settings-item">
          <label>静默阈值 (帧)</label>
          <input type="number" id="s-silent-threshold" value="${c.silent_threshold || 5}" min="1" max="30">
        </div>
        <div class="settings-item">
          <label>识别区域</label>
          <select id="s-capture-region">
            <option value="fullscreen" ${c.capture_region === 'fullscreen' ? 'selected' : ''}>全屏</option>
            <option value="window" ${c.capture_region === 'window' ? 'selected' : ''}>窗口</option>
          </select>
        </div>
      </div>
    `;
  }

  _renderDanmaku() {
    const c = this.config.danmaku || {};
    return `
      <div class="settings-group">
        <h3>弹幕设置</h3>
        <div class="settings-item">
          <label>自动弹幕</label>
          <input type="checkbox" id="s-danmaku-auto" ${c.auto_enabled ? 'checked' : ''}>
        </div>
        <div class="settings-item">
          <label>鼓励间隔 (秒)</label>
          <input type="number" id="s-danmaku-interval" value="${c.encouragement_interval || 30}" min="5" max="300">
        </div>
        <div class="settings-item">
          <label>风格</label>
          <select id="s-danmaku-style">
            <option value="auto" ${c.style === 'auto' ? 'selected' : ''}>自动匹配</option>
            <option value="encouragement" ${c.style === 'encouragement' ? 'selected' : ''}>鼓励</option>
            <option value="tutorial" ${c.style === 'tutorial' ? 'selected' : ''}>教程</option>
            <option value="comment" ${c.style === 'comment' ? 'selected' : ''}>吐槽</option>
          </select>
        </div>
      </div>
    `;
  }

  _renderSearch() {
    const c = this.config.search || {};
    return `
      <div class="settings-group">
        <h3>搜索设置</h3>
        <div class="settings-item">
          <label>搜索引擎</label>
          <select id="s-search-engine">
            <option value="duckduckgo" ${c.engine === 'duckduckgo' ? 'selected' : ''}>DuckDuckGo (免费)</option>
            <option value="searxng" ${c.engine === 'searxng' ? 'selected' : ''}>SearXNG (自托管)</option>
          </select>
        </div>
        <div class="settings-item">
          <label>API 地址 (SearXNG)</label>
          <input type="text" id="s-search-url" value="${c.api_url || ''}" placeholder="http://localhost:8888">
        </div>
      </div>
    `;
  }

  _renderMemory() {
    const c = this.config.memory || {};
    return `
      <div class="settings-group">
        <h3>记忆设置</h3>
        <div class="settings-item">
          <label>向量 API 地址</label>
          <input type="text" id="s-mem-vector-url" value="${c.vector?.api_url || ''}">
        </div>
        <div class="settings-item">
          <label>向量 API Key</label>
          <input type="text" id="s-mem-vector-key" value="${c.vector?.api_key || ''}">
        </div>
        <div class="settings-item">
          <label>Top K</label>
          <input type="number" id="s-mem-topk" value="${c.top_k || 20}" min="5" max="50">
        </div>
        <div class="settings-item">
          <label>Top N</label>
          <input type="number" id="s-mem-topn" value="${c.top_n || 8}" min="3" max="20">
        </div>
      </div>
    `;
  }

  _save() {
    // 收集当前配置
    const config = this._collectConfig();

    // 发送到后端
    if (window.wsClient && window.wsClient.isConnected) {
      window.wsClient.send('settings.save', { config });
    }

    this.hide();
  }

  _collectConfig() {
    // 收集所有设置项的值
    const config = JSON.parse(JSON.stringify(this.config));

    // 通用
    config.general = config.general || {};
    config.general.auto_launch = this._getVal('s-auto-launch', 'checkbox');
    config.general.language = this._getVal('s-language');

    // UI
    config.ui = config.ui || {};
    config.ui.opacity = parseInt(this._getVal('s-opacity', 'range') || 90);
    config.ui.theme = this._getVal('s-theme');

    // AI
    config.ai = config.ai || {};
    config.ai.provider = this._getVal('s-ai-provider');
    config.ai.api_url = this._getVal('s-ai-url');
    config.ai.api_key = this._getVal('s-ai-key');
    config.ai.model = this._getVal('s-ai-model');
    config.ai.temperature = parseFloat(this._getVal('s-ai-temp') || 0.7);

    // Game
    config.game = config.game || {};
    config.game.capture_fps = parseFloat(this._getVal('s-capture-fps') || 1);
    config.game.silent_fps = parseFloat(this._getVal('s-silent-fps') || 0.2);
    config.game.silent_threshold = parseInt(this._getVal('s-silent-threshold') || 5);

    // Search
    config.search = config.search || {};
    config.search.engine = this._getVal('s-search-engine');
    config.search.api_url = this._getVal('s-search-url');

    return config;
  }

  _getVal(id, type = 'value') {
    const el = this.element.querySelector(`#${id}`);
    if (!el) return null;
    if (type === 'checkbox') return el.checked;
    return el.value;
  }

  _export() {
    const config = this._collectConfig();
    const blob = new Blob([JSON.stringify(config, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'game-companion-config.json';
    a.click();
    URL.revokeObjectURL(url);
  }

  _import() {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.json';
    input.onchange = (e) => {
      const file = e.target.files[0];
      if (file) {
        const reader = new FileReader();
        reader.onload = (ev) => {
          try {
            const config = JSON.parse(ev.target.result);
            this.setConfig(config);
            this._save();
          } catch (err) {
            alert('配置文件格式错误');
          }
        };
        reader.readAsText(file);
      }
    };
    input.click();
  }

  show() {
    this.element.classList.remove('hidden');
    this.visible = true;
    this.loadConfig();
    if (window.ipcRenderer) {
      window.ipcRenderer.send('set-ignore-mouse-events', false);
    }
  }

  hide() {
    this.element.classList.add('hidden');
    this.visible = false;
    if (window.ipcRenderer) {
      window.ipcRenderer.send('set-ignore-mouse-events', true, { forward: true });
    }
  }

  toggle() {
    if (this.visible) {
      this.hide();
    } else {
      this.show();
    }
  }
}

window.SettingsPanel = SettingsPanel;
