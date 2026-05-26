<template>
  <div class="login-page">
    <!-- 动态粒子背景 -->
    <div class="particles-container">
      <div
        v-for="n in 30"
        :key="n"
        class="particle"
        :style="getParticleStyle(n)"
      ></div>
    </div>

    <!-- 光晕背景 -->
    <div class="glow-bg">
      <div class="glow-orb glow-1"></div>
      <div class="glow-orb glow-2"></div>
      <div class="glow-orb glow-3"></div>
    </div>

    <!-- 登录卡片 -->
    <div class="login-card-wrapper">
      <div class="login-card">
        <div class="card-shine"></div>
        <div class="login-header">
          <div class="logo-orbit">
            <div class="logo-core">
              <el-icon :size="32" color="#fff"><Picture /></el-icon>
            </div>
            <div class="orbit-ring"></div>
          </div>
          <h1 class="login-title">
            <span class="title-main">LUCS</span>
            <span class="title-sub">Platform</span>
          </h1>
          <p class="login-subtitle">土地利用分类智能检测平台</p>
          <p class="login-desc">遥感影像 · AI智能分类 · 精准识别</p>
        </div>

        <el-form
          ref="loginFormRef"
          :model="loginForm"
          :rules="loginRules"
          class="login-form"
        >
          <el-form-item prop="username">
            <div class="input-wrapper">
              <el-icon class="input-icon"><User /></el-icon>
              <el-input
                v-model="loginForm.username"
                placeholder="请输入用户名"
                size="large"
                class="neon-input"
              />
            </div>
          </el-form-item>

          <el-form-item prop="password">
            <div class="input-wrapper">
              <el-icon class="input-icon"><Lock /></el-icon>
              <el-input
                v-model="loginForm.password"
                type="password"
                placeholder="请输入密码"
                size="large"
                class="neon-input"
                show-password
              />
            </div>
          </el-form-item>

          <el-form-item class="form-actions">
            <el-checkbox v-model="loginForm.remember" class="remember-check">
              <span class="check-text">记住我</span>
            </el-checkbox>
            <router-link to="/forgot-password" class="forgot-password">忘记密码?</router-link>
          </el-form-item>

          <el-form-item>
            <button type="button" class="login-btn" @click="handleLogin">
              <span class="btn-text">登 录</span>
              <div class="btn-glow"></div>
            </button>
          </el-form-item>
        </el-form>

        <div class="register-link">
          <span>还没有账号？</span>
          <router-link to="/register">立即注册</router-link>
        </div>
      </div>

      <!-- 底部装饰 -->
      <div class="login-footer">
        <div class="tech-line">
          <span class="line-segment"></span>
          <span class="line-dot"></span>
          <span class="line-segment"></span>
        </div>
        <p class="footer-text">多场景遥感影像智能分类系统 v2.0</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from "vue";
import { Picture, User, Lock } from "@element-plus/icons-vue";
import { useRouter } from "vue-router";

const router = useRouter();

const loginForm = reactive({
  username: "",
  password: "",
  remember: false,
});

const loginRules = {
  username: [
    { required: true, message: "请输入用户名", trigger: "blur" },
    { min: 3, max: 20, message: "用户名长度在3到20个字符", trigger: "blur" },
  ],
  password: [
    { required: true, message: "请输入密码", trigger: "blur" },
    { min: 6, max: 30, message: "密码长度在6到30个字符", trigger: "blur" },
  ],
};

const loginFormRef = ref(null);

const handleLogin = () => {
  loginFormRef.value.validate((valid) => {
    if (valid) {
      localStorage.setItem("token", "mock-token");
      router.push("/detection");
    }
  });
};

const getParticleStyle = (n) => {
  const size = Math.random() * 4 + 1;
  const left = Math.random() * 100;
  const delay = Math.random() * 8;
  const duration = Math.random() * 6 + 6;
  const opacity = Math.random() * 0.5 + 0.1;
  return {
    width: `${size}px`,
    height: `${size}px`,
    left: `${left}%`,
    animationDelay: `${delay}s`,
    animationDuration: `${duration}s`,
    opacity,
  };
};
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-primary);
  position: relative;
  overflow: hidden;
}

/* 粒子背景 */
.particles-container {
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 0;
}
.particle {
  position: absolute;
  bottom: -10px;
  border-radius: 50%;
  background: var(--accent-cyan);
  animation: float-up linear infinite;
}
@keyframes float-up {
  0% {
    transform: translateY(0) scale(1);
    opacity: 0;
  }
  10% {
    opacity: var(--particle-opacity, 0.3);
  }
  90% {
    opacity: var(--particle-opacity, 0.3);
  }
  100% {
    transform: translateY(-100vh) scale(0.5);
    opacity: 0;
  }
}

/* 光晕背景 */
.glow-bg {
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 0;
}
.glow-orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(100px);
  opacity: 0.12;
  animation: orb-drift 25s ease-in-out infinite;
}
.glow-1 {
  width: 500px;
  height: 500px;
  background: var(--accent-cyan);
  top: -100px;
  left: -100px;
}
.glow-2 {
  width: 600px;
  height: 600px;
  background: var(--accent-purple);
  bottom: -200px;
  right: -150px;
  animation-delay: -8s;
}
.glow-3 {
  width: 400px;
  height: 400px;
  background: var(--accent-pink);
  top: 40%;
  left: 40%;
  animation-delay: -16s;
}
@keyframes orb-drift {
  0%, 100% { transform: translate(0, 0) scale(1); }
  33% { transform: translate(50px, -60px) scale(1.15); }
  66% { transform: translate(-40px, 40px) scale(0.9); }
}

/* 登录卡片 */
.login-card-wrapper {
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.login-card {
  width: 420px;
  max-width: 90vw;
  padding: 48px 40px;
  background: var(--bg-card);
  backdrop-filter: blur(30px) saturate(1.5);
  -webkit-backdrop-filter: blur(30px) saturate(1.5);
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius-xl);
  position: relative;
  overflow: hidden;
  animation: fadeInUp 0.8s ease-out;
}
.card-shine {
  position: absolute;
  top: 0;
  left: -100%;
  width: 60%;
  height: 100%;
  background: linear-gradient(
    90deg,
    transparent,
    rgba(255, 255, 255, 0.03),
    transparent
  );
  animation: shimmer 6s ease-in-out infinite;
  pointer-events: none;
}

.login-header {
  text-align: center;
  margin-bottom: 36px;
}

.logo-orbit {
  position: relative;
  width: 72px;
  height: 72px;
  margin: 0 auto 20px;
}
.logo-core {
  position: absolute;
  inset: 8px;
  background: var(--accent-gradient);
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: var(--accent-glow);
  z-index: 2;
}
.orbit-ring {
  position: absolute;
  inset: 0;
  border: 1px dashed rgba(6, 182, 212, 0.3);
  border-radius: 50%;
  animation: spin-slow 12s linear infinite;
}
.orbit-ring::after {
  content: '';
  position: absolute;
  top: -2px;
  left: 50%;
  width: 4px;
  height: 4px;
  background: var(--accent-cyan);
  border-radius: 50%;
  box-shadow: 0 0 8px var(--accent-cyan);
}

.login-title {
  font-size: 26px;
  font-weight: 700;
  margin-bottom: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
}
.title-main {
  color: var(--text-heading);
}
.title-sub {
  background: var(--accent-gradient);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
.login-subtitle {
  font-size: 15px;
  color: var(--text-secondary);
  margin-bottom: 4px;
  font-weight: 500;
}
.login-desc {
  font-size: 12px;
  color: var(--text-muted);
  letter-spacing: 2px;
  text-transform: uppercase;
}

/* 输入框 */
.input-wrapper {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 0 14px;
  background: rgba(15, 23, 42, 0.6);
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius-md);
  transition: all 0.3s;
}
.input-wrapper:focus-within {
  border-color: var(--accent-cyan);
  box-shadow: 0 0 0 3px rgba(6, 182, 212, 0.1), 0 0 16px rgba(6, 182, 212, 0.1);
}
.input-icon {
  font-size: 16px;
  color: var(--text-muted);
  flex-shrink: 0;
}
:deep(.neon-input .el-input__wrapper) {
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
  padding: 0 !important;
}
:deep(.neon-input .el-input__inner) {
  height: 48px;
  color: var(--text-primary) !important;
}
:deep(.neon-input .el-input__inner::placeholder) {
  color: var(--text-muted) !important;
}

/* 表单操作 */
.form-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}
.remember-check :deep(.el-checkbox__input.is-checked .el-checkbox__inner) {
  background: var(--accent-gradient) !important;
  border-color: transparent !important;
}
.check-text {
  font-size: 13px;
  color: var(--text-secondary);
}
.forgot-password {
  font-size: 13px;
  color: var(--accent-cyan);
  transition: all 0.3s;
}
.forgot-password:hover {
  color: var(--accent-purple);
  text-shadow: 0 0 8px rgba(139, 92, 246, 0.3);
}

/* 登录按钮 */
.login-btn {
  width: 100%;
  height: 50px;
  border: none;
  border-radius: var(--border-radius-md);
  background: var(--accent-gradient);
  background-size: 200% 100%;
  color: white;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  transition: all 0.3s;
  box-shadow: 0 4px 20px rgba(6, 182, 212, 0.3);
  animation: gradient-shift 4s ease infinite;
}
.login-btn:hover {
  box-shadow: 0 6px 30px rgba(6, 182, 212, 0.5), 0 0 50px rgba(139, 92, 246, 0.2);
  transform: translateY(-2px);
}
.login-btn:active {
  transform: translateY(0);
}
.btn-text {
  position: relative;
  z-index: 1;
}
.btn-glow {
  position: absolute;
  inset: 0;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.15), transparent);
  transform: translateX(-100%);
  transition: transform 0.6s;
}
.login-btn:hover .btn-glow {
  transform: translateX(100%);
}

/* 注册链接 */
.register-link {
  text-align: center;
  margin-top: 24px;
  font-size: 13px;
  color: var(--text-muted);
}
.register-link a {
  color: var(--accent-cyan);
  margin-left: 4px;
  font-weight: 500;
  transition: all 0.3s;
}
.register-link a:hover {
  color: var(--accent-purple);
  text-shadow: 0 0 8px rgba(139, 92, 246, 0.3);
}

/* 底部装饰 */
.login-footer {
  margin-top: 32px;
  text-align: center;
}
.tech-line {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  margin-bottom: 12px;
}
.line-segment {
  width: 40px;
  height: 1px;
  background: linear-gradient(90deg, transparent, var(--border-glow), transparent);
}
.line-dot {
  width: 4px;
  height: 4px;
  border-radius: 50%;
  background: var(--accent-cyan);
  box-shadow: 0 0 8px var(--accent-cyan);
}
.footer-text {
  font-size: 11px;
  color: var(--text-muted);
  letter-spacing: 1px;
}
</style>
