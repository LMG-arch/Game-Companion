// frontend/main/shortcuts.js
/**
 * 全局快捷键注册
 */

const { globalShortcut } = require('electron');

class Shortcuts {
  constructor() {
    this.shortcuts = {};
  }

  /**
   * 注册所有快捷键
   * @param {object} handlers - 快捷键处理函数
   */
  register(handlers) {
    // Ctrl+Shift+Space: 呼出/隐藏输入框
    this._register('Ctrl+Shift+Space', handlers.toggleInput || (() => {}));

    // Ctrl+Shift+H: 隐藏/显示所有 UI
    this._register('Ctrl+Shift+H', handlers.toggleUI || (() => {}));

    // Ctrl+Shift+S: 打开设置
    this._register('Ctrl+Shift+S', handlers.openSettings || (() => {}));

    // Ctrl+Shift+D: 弹幕开关
    this._register('Ctrl+Shift+D', handlers.toggleDanmaku || (() => {}));
  }

  _register(accelerator, callback) {
    try {
      const ret = globalShortcut.register(accelerator, callback);
      if (ret) {
        this.shortcuts[accelerator] = callback;
        console.log(`快捷键已注册: ${accelerator}`);
      } else {
        console.error(`快捷键注册失败: ${accelerator}`);
      }
    } catch (e) {
      console.error(`快捷键注册错误: ${accelerator}`, e);
    }
  }

  /**
   * 注销所有快捷键
   */
  unregisterAll() {
    globalShortcut.unregisterAll();
    this.shortcuts = {};
    console.log('所有快捷键已注销');
  }
}

module.exports = Shortcuts;
