// frontend/main/python-manager.js
/**
 * Python 进程管理模块
 * 负责启动、监控、关闭 Python 子进程
 */

const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

class PythonManager {
  constructor() {
    this.process = null;
    this.portFile = path.join(process.env.TEMP || '/tmp', 'game-companion-port.txt');
    this.backendPath = path.join(__dirname, '..', '..', 'backend');
  }

  /**
   * 启动 Python 子进程
   * @returns {Promise<void>}
   */
  start() {
    return new Promise((resolve, reject) => {
      // 清理旧的端口文件
      if (fs.existsSync(this.portFile)) {
        fs.unlinkSync(this.portFile);
      }

      // 启动 Python 进程
      this.process = spawn('python', ['-m', 'backend.main'], {
        cwd: path.join(__dirname, '..', '..'),
        stdio: ['pipe', 'pipe', 'pipe'],
        shell: true
      });

      // 监听输出
      this.process.stdout.on('data', (data) => {
        const output = data.toString().trim();
        if (output) {
          console.log(`[Python] ${output}`);
        }
      });

      this.process.stderr.on('data', (data) => {
        const output = data.toString().trim();
        if (output) {
          console.error(`[Python Error] ${output}`);
        }
      });

      // 监听进程退出
      this.process.on('exit', (code) => {
        console.log(`Python 进程已退出，退出码: ${code}`);
        this.process = null;
      });

      // 等待端口文件出现（最多 10 秒）
      let attempts = 0;
      const checkPort = setInterval(() => {
        attempts++;
        if (fs.existsSync(this.portFile)) {
          clearInterval(checkPort);
          resolve();
        } else if (attempts > 100) {
          clearInterval(checkPort);
          reject(new Error('Python 启动超时'));
        }
      }, 100);
    });
  }

  /**
   * 读取 Python 写入的端口号
   * @returns {number|null}
   */
  getPort() {
    try {
      if (fs.existsSync(this.portFile)) {
        return parseInt(fs.readFileSync(this.portFile, 'utf-8').trim());
      }
    } catch (e) {
      console.error('读取端口文件失败:', e);
    }
    return null;
  }

  /**
   * 关闭 Python 子进程
   */
  async shutdown() {
    if (this.process) {
      // 尝试发送关闭消息（通过 stdin）
      try {
        this.process.stdin.write('shutdown\n');
      } catch (e) {
        // 忽略
      }

      // 等待 2 秒，如果还没退出就强制 kill
      await new Promise((resolve) => {
        const timeout = setTimeout(() => {
          if (this.process) {
            this.process.kill('SIGTERM');
          }
          resolve();
        }, 2000);

        this.process.on('exit', () => {
          clearTimeout(timeout);
          resolve();
        });
      });

      this.process = null;
    }
  }

  /**
   * 检查 Python 进程是否在运行
   * @returns {boolean}
   */
  isRunning() {
    return this.process !== null;
  }
}

module.exports = PythonManager;
