/**
 * 一键同时启动后端 + 前端
 * 用法: node scripts/dev-all.js
 */
import { spawn } from 'child_process';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const projectRoot = path.resolve(__dirname, '..', '..');
const backendDir = path.join(projectRoot, 'backend');
const frontendDir = path.join(projectRoot, 'frontend');

// 颜色代码
const CYAN = '\x1b[36m';
const BLUE = '\x1b[34m';
const RESET = '\x1b[0m';

// Python 解释器路径（根据你的 conda 环境修改）
const PYTHON = 'D:\\Anaconda\\envs\\rsod-web\\python.exe';

console.log('============================================');
console.log('  LUCS Platform 一键启动');
console.log('============================================\n');

// 启动后端
const backend = spawn(PYTHON, [
  '-m', 'uvicorn', 'main:app',
  '--host', '0.0.0.0',
  '--port', '8000'
], {
  cwd: backendDir,
  shell: true,
  stdio: ['inherit', 'pipe', 'pipe']
});

// 启动前端（延迟 2 秒，等后端先起）
setTimeout(() => {
  const frontend = spawn('npm', ['run', 'dev'], {
    cwd: frontendDir,
    shell: true,
    stdio: ['inherit', 'pipe', 'pipe']
  });

  frontend.stdout.on('data', (data) => {
    process.stdout.write(`${BLUE}[FRONTEND]${RESET} ${data}`);
  });

  frontend.stderr.on('data', (data) => {
    process.stderr.write(`${BLUE}[FRONTEND]${RESET} ${data}`);
  });

  frontend.on('close', (code) => {
    console.log(`\n${BLUE}[FRONTEND]${RESET} 进程退出，代码: ${code}`);
    backend.kill();
    process.exit(code || 0);
  });
}, 2000);

// 后端输出
backend.stdout.on('data', (data) => {
  process.stdout.write(`${CYAN}[BACKEND]${RESET} ${data}`);
});

backend.stderr.on('data', (data) => {
  process.stderr.write(`${CYAN}[BACKEND]${RESET} ${data}`);
});

backend.on('close', (code) => {
  console.log(`\n${CYAN}[BACKEND]${RESET} 进程退出，代码: ${code}`);
  process.exit(code || 0);
});

// Ctrl+C 优雅退出
process.on('SIGINT', () => {
  console.log('\n\n收到终止信号，正在关闭服务...');
  backend.kill('SIGINT');
  process.exit(0);
});

process.on('SIGTERM', () => {
  backend.kill('SIGTERM');
  process.exit(0);
});

console.log(`${CYAN}[BACKEND]${RESET} 正在启动...`);
console.log(`${BLUE}[FRONTEND]${RESET} 将在 2 秒后启动...\n`);
