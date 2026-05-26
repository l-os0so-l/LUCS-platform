<template>
  <div class="register-page">
    <!-- 动态背景 -->
    <div class="particles-container">
      <div v-for="n in 25" :key="n" class="particle" :style="getParticleStyle(n)"></div>
    </div>
    <div class="glow-bg">
      <div class="glow-orb glow-1"></div>
      <div class="glow-orb glow-2"></div>
    </div>

    <div class="register-card-wrapper">
      <div class="register-card">
        <div class="card-shine"></div>
        <div class="register-header">
          <div class="logo-orbit">
            <div class="logo-core">
              <el-icon :size="28" color="#fff"><UserFilled /></el-icon>
            </div>
            <div class="orbit-ring"></div>
          </div>
          <h1 class="register-title">
            <span class="title-main">创建账号</span>
          </h1>
          <p class="register-subtitle">加入我们，开始智能分类之旅</p>
          <p class="register-desc">遥感影像 · AI智能分类 · 精准识别</p>
        </div>

        <el-form
          ref="registerFormRef"
          :model="registerForm"
          :rules="registerRules"
          class="register-form"
        >
          <el-form-item prop="username">
            <div class="input-wrapper">
              <el-icon class="input-icon"><User /></el-icon>
              <el-input v-model="registerForm.username" placeholder="请输入用户名" size="large" class="neon-input" />
            </div>
          </el-form-item>

          <el-form-item prop="email">
            <div class="input-wrapper">
              <el-icon class="input-icon"><Message /></el-icon>
              <el-input v-model="registerForm.email" type="email" placeholder="请输入邮箱" size="large" class="neon-input" />
            </div>
          </el-form-item>

          <el-form-item prop="password">
            <div class="input-wrapper">
              <el-icon class="input-icon"><Lock /></el-icon>
              <el-input v-model="registerForm.password" type="password" placeholder="请输入密码" size="large" class="neon-input" show-password />
            </div>
          </el-form-item>

          <el-form-item prop="confirmPassword">
            <div class="input-wrapper">
              <el-icon class="input-icon"><Lock /></el-icon>
              <el-input v-model="registerForm.confirmPassword" type="password" placeholder="请确认密码" size="large" class="neon-input" show-password />
            </div>
          </el-form-item>

          <el-form-item class="agree-terms">
            <el-checkbox v-model="registerForm.agree" class="remember-check">
              <span class="check-text">我已阅读并同意</span>
            </el-checkbox>
            <a href="#" class="terms-link">《服务条款》</a>
            <span class="check-text">和</span>
            <a href="#" class="terms-link">《隐私政策》</a>
          </el-form-item>

          <el-form-item>
            <button type="button" class="register-btn" @click="handleRegister">
              <span class="btn-text">注 册</span>
              <div class="btn-glow"></div>
            </button>
          </el-form-item>
        </el-form>

        <div class="login-link">
          <span>已有账号？</span>
          <router-link to="/login">立即登录</router-link>
        </div>
      </div>

      <div class="register-footer">
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
import { UserFilled, User, Message, Lock } from "@element-plus/icons-vue";
import { useRouter } from "vue-router";

const router = useRouter();

const registerForm = reactive({
  username: "",
  email: "",
  password: "",
  confirmPassword: "",
  agree: false,
});

const registerRules = {
  username: [
    { required: true, message: "请输入用户名", trigger: "blur" },
    { min: 3, max: 20, message: "用户名长度在3到20个字符", trigger: "blur" },
    { pattern: /^[a-zA-Z0-9_]+$/, message: "用户名只能包含字母、数字和下划线", trigger: "blur" },
  ],
  email: [
    { required: true, message: "请输入邮箱", trigger: "blur" },
    { type: "email", message: "请输入正确的邮箱格式", trigger: "blur" },
  ],
  password: [
    { required: true, message: "请输入密码", trigger: "blur" },
    { min: 6, max: 30, message: "密码长度在6到30个字符", trigger: "blur" },
    { pattern: /^(?=.*[a-zA-Z])(?=.*\d)/, message: "密码需包含字母和数字", trigger: "blur" },
  ],
  confirmPassword: [
    { required: true, message: "请确认密码", trigger: "blur" },
    {
      validator: (rule, value, callback) => {
        if (value !== registerForm.password) callback(new Error("两次输入的密码不一致"));
        else callback();
      },
      trigger: "blur",
    },
  ],
  agree: [
    {
      validator: (rule, value, callback) => {
        if (!value) callback(new Error("请同意服务条款和隐私政策"));
        else callback();
      },
      trigger: "change",
    },
  ],
};

const registerFormRef = ref(null);

const handleRegister = () => {
  registerFormRef.value.validate((valid) => {
    if (valid) {
      localStorage.setItem("token", "mock-token");
      router.push("/detection");
    }
  });
};

const getParticleStyle = (n) => {
  const size = Math.random() * 3 + 1;
  return {
    width: `${size}px`,
    height: `${size}px`,
    left: `${Math.random() * 100}%`,
    animationDelay: `${Math.random() * 8}s`,
    animationDuration: `${Math.random() * 6 + 6}s`,
    opacity: Math.random() * 0.4 + 0.1,
  };
};
</script>

<style scoped>
.register-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-primary);
  position: relative;
  overflow: hidden;
  padding: 40px 0;
}

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
  0% { transform: translateY(0) scale(1); opacity: 0; }
  10% { opacity: var(--particle-opacity, 0.3); }
  90% { opacity: var(--particle-opacity, 0.3); }
  100% { transform: translateY(-100vh) scale(0.5); opacity: 0; }
}

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
.glow-1 { width: 500px; height: 500px; background: var(--accent-cyan); top: -100px; left: -100px; }
.glow-2 { width: 600px; height: 600px; background: var(--accent-purple); bottom: -200px; right: -150px; animation-delay: -10s; }
@keyframes orb-drift {
  0%, 100% { transform: translate(0, 0) scale(1); }
  33% { transform: translate(50px, -60px) scale(1.15); }
  66% { transform: translate(-40px, 40px) scale(0.9); }
}

.register-card-wrapper {
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.register-card {
  width: 440px;
  max-width: 90vw;
  padding: 40px 36px;
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
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.03), transparent);
  animation: shimmer 6s ease-in-out infinite;
  pointer-events: none;
}

.register-header {
  text-align: center;
  margin-bottom: 28px;
}
.logo-orbit {
  position: relative;
  width: 64px;
  height: 64px;
  margin: 0 auto 16px;
}
.logo-core {
  position: absolute;
  inset: 6px;
  background: var(--accent-gradient);
  border-radius: 14px;
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

.register-title {
  font-size: 24px;
  font-weight: 700;
  margin-bottom: 6px;
}
.title-main {
  color: var(--text-heading);
}
.register-subtitle {
  font-size: 14px;
  color: var(--text-secondary);
  margin-bottom: 3px;
}
.register-desc {
  font-size: 11px;
  color: var(--text-muted);
  letter-spacing: 2px;
  text-transform: uppercase;
}

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
  height: 46px;
  color: var(--text-primary) !important;
}
:deep(.neon-input .el-input__inner::placeholder) {
  color: var(--text-muted) !important;
}

.agree-terms {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 4px;
  font-size: 12px;
  margin-bottom: 8px;
}
.remember-check :deep(.el-checkbox__input.is-checked .el-checkbox__inner) {
  background: var(--accent-gradient) !important;
  border-color: transparent !important;
}
.check-text {
  font-size: 12px;
  color: var(--text-muted);
}
.terms-link {
  color: var(--accent-cyan);
  font-size: 12px;
  transition: all 0.3s;
}
.terms-link:hover {
  color: var(--accent-purple);
}

.register-btn {
  width: 100%;
  height: 48px;
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
.register-btn:hover {
  box-shadow: 0 6px 30px rgba(6, 182, 212, 0.5), 0 0 50px rgba(139, 92, 246, 0.2);
  transform: translateY(-2px);
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
.register-btn:hover .btn-glow {
  transform: translateX(100%);
}

.login-link {
  text-align: center;
  margin-top: 20px;
  font-size: 13px;
  color: var(--text-muted);
}
.login-link a {
  color: var(--accent-cyan);
  margin-left: 4px;
  font-weight: 500;
  transition: all 0.3s;
}
.login-link a:hover {
  color: var(--accent-purple);
}

.register-footer {
  margin-top: 28px;
  text-align: center;
}
.tech-line {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  margin-bottom: 10px;
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
