// frontend/renderer/components/ChatInput.js
/**
 * 输入框组件
 * 快捷键呼出，用户输入问题
 */

class ChatInput {
  constructor() {
    this.element = null;
    this.visible = false;
    this.onSubmit = null;
    this.init();
  }

  init() {
    this.element = document.createElement('div');
    this.element.id = 'chat-input';
    this.element.className = 'hidden';
    this.element.style.cssText = `
      position: fixed;
      bottom: 20px;
      left: 50%;
      transform: translateX(-50%);
      width: 500px;
      z-index: 60;
    `;

    this.element.innerHTML = `
      <div style="
        background: rgba(0, 0, 0, 0.9);
        border-radius: 12px;
        padding: 12px;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.5);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
      ">
        <div style="display: flex; gap: 8px;">
          <input type="text" id="chat-text" placeholder="输入问题..." style="
            flex: 1;
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 8px;
            padding: 10px 14px;
            color: white;
            font-size: 14px;
            outline: none;
            font-family: 'Microsoft YaHei', sans-serif;
          ">
          <button id="chat-submit" style="
            background: #2196f3;
            color: white;
            border: none;
            border-radius: 8px;
            padding: 10px 20px;
            cursor: pointer;
            font-size: 14px;
          ">发送</button>
        </div>
      </div>
    `;

    document.body.appendChild(this.element);

    // 注册到点击穿透模块
    if (window.clickThrough) {
    }

    // 事件绑定
    const input = this.element.querySelector('#chat-text');
    const submitBtn = this.element.querySelector('#chat-submit');

    submitBtn.addEventListener('click', () => this._submit());

    input.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') {
        this._submit();
      } else if (e.key === 'Escape') {
        this.hide();
      }
    });
  }

  _submit() {
    const input = this.element.querySelector('#chat-text');
    const text = input.value.trim();
    if (text && this.onSubmit) {
      this.onSubmit(text);
      input.value = '';
      this.hide();
    }
  }

  show() {
    this.element.classList.remove('hidden');
    this.visible = true;
    const input = this.element.querySelector('#chat-text');
    if (input) {
      input.focus();
    }
    // 禁用穿透
    if (window.clickThrough) {
      window.clickThrough.disable();
    }
  }

  hide() {
    this.element.classList.add('hidden');
    this.visible = false;
    // 恢复穿透
    if (window.clickThrough) {
      window.clickThrough.enable();
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

window.ChatInput = ChatInput;
