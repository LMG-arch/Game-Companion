// frontend/renderer/components/PersonalityEditor.js
/**
 * 人格编辑器组件
 * 编辑人格属性、切换人格
 */

class PersonalityEditor {
  constructor() {
    this.element = null;
    this.visible = false;
    this.personalities = [];
    this.activeId = '';
    this.init();
  }

  init() {
    this.element = document.createElement('div');
    this.element.id = 'personality-editor';
    this.element.className = 'hidden';
    this.element.style.cssText = `
      position: fixed;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
      width: 500px;
      max-height: 80vh;
      background: rgba(0, 0, 0, 0.95);
      border-radius: 12px;
      padding: 20px;
      z-index: 100;
      overflow-y: auto;
      backdrop-filter: blur(10px);
      border: 1px solid rgba(255, 255, 255, 0.2);
      pointer-events: auto;
    `;

    this.element.innerHTML = `
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
        <h2 style="font-size: 18px; color: #fff;">🎭 人格编辑器</h2>
        <button id="close-personality-editor" style="background: none; border: none; color: #fff; font-size: 20px; cursor: pointer;">✕</button>
      </div>

      <div style="margin-bottom: 16px;">
        <h3 style="font-size: 14px; color: rgba(255,255,255,0.8); margin-bottom: 8px;">切换人格</h3>
        <div id="personality-list" style="display: flex; flex-wrap: wrap; gap: 8px;"></div>
      </div>

      <div style="margin-bottom: 16px;">
        <h3 style="font-size: 14px; color: rgba(255,255,255,0.8); margin-bottom: 8px;">生成新人格</h3>
        <div style="display: flex; gap: 8px;">
          <input type="text" id="personality-keywords" placeholder="输入关键词（如：傲娇、猫耳、元气）" style="
            flex: 1;
            background: rgba(255,255,255,0.1);
            border: 1px solid rgba(255,255,255,0.2);
            border-radius: 8px;
            padding: 8px 12px;
            color: white;
            font-size: 13px;
            outline: none;
          ">
          <button id="generate-personality" class="btn" style="padding: 8px 16px; font-size: 13px;">生成</button>
        </div>
      </div>

      <div id="personality-detail" style="display: none;">
        <h3 style="font-size: 14px; color: rgba(255,255,255,0.8); margin-bottom: 8px;">当前人格</h3>
        <div style="background: rgba(255,255,255,0.05); border-radius: 8px; padding: 12px;">
          <p id="detail-name" style="font-size: 16px; color: #fff; margin-bottom: 4px;"></p>
          <p id="detail-title" style="font-size: 12px; color: rgba(255,255,255,0.6); margin-bottom: 8px;"></p>
          <p id="detail-background" style="font-size: 13px; color: rgba(255,255,255,0.8); line-height: 1.6;"></p>
        </div>
      </div>
    `;

    document.body.appendChild(this.element);

    // 事件绑定
    this.element.querySelector('#close-personality-editor').addEventListener('click', () => {
      this.hide();
    });

    this.element.querySelector('#generate-personality').addEventListener('click', () => {
      this._generate();
    });
  }

  async loadPersonalities() {
    // 通过 WebSocket 请求人格列表
    if (window.wsClient && window.wsClient.isConnected) {
      window.wsClient.send('personality.list');
    }
  }

  setPersonalities(list, activeId) {
    this.personalities = list;
    this.activeId = activeId;
    this._renderList();
    this._updateDetail();
  }

  _renderList() {
    const container = this.element.querySelector('#personality-list');
    if (!container) return;

    container.innerHTML = this.personalities.map(p => {
      const isActive = p.id === this.activeId;
      return `
        <button data-id="${p.id}" style="
          padding: 6px 12px;
          background: ${isActive ? '#2196f3' : 'rgba(255,255,255,0.1)'};
          color: white;
          border: none;
          border-radius: 6px;
          cursor: pointer;
          font-size: 12px;
        ">${p.name}</button>
      `;
    }).join('');

    // 点击切换
    container.querySelectorAll('button').forEach(btn => {
      btn.addEventListener('click', () => {
        const id = btn.dataset.id;
        if (window.wsClient && window.wsClient.isConnected) {
          window.wsClient.send('personality.switch', { id });
        }
      });
    });
  }

  _updateDetail() {
    const active = this.personalities.find(p => p.id === this.activeId);
    const detail = this.element.querySelector('#personality-detail');
    if (!active || !detail) {
      if (detail) detail.style.display = 'none';
      return;
    }

    detail.style.display = 'block';
    this.element.querySelector('#detail-name').textContent = active.name;
    this.element.querySelector('#detail-title').textContent = active.title;
    this.element.querySelector('#detail-background').textContent = active.background || '';
  }

  async _generate() {
    const input = this.element.querySelector('#personality-keywords');
    const keywords = input.value.trim();
    if (!keywords) return;

    if (window.wsClient && window.wsClient.isConnected) {
      window.wsClient.send('personality.generate', { keywords });
    }
  }

  show() {
    this.element.classList.remove('hidden');
    this.visible = true;
    this.loadPersonalities();
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

window.PersonalityEditor = PersonalityEditor;
