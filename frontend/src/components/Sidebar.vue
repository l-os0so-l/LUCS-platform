<template>
  <div class="sidebar-container">
    <!-- Logo 区域 -->
    <div class="logo-section">
      <div class="logo-glow"></div>
      <div class="logo-icon">
        <Monitor style="color: white; font-size: 22px" />
      </div>
      <div class="logo-text">
        <div class="logo-title">LUCS<span class="title-accent">Platform</span></div>
        <div class="logo-subtitle">智能遥感分类系统</div>
      </div>
    </div>

    <!-- 导航菜单 -->
    <div class="nav-menu">
      <div class="menu-label">功能导航</div>
      <div
        v-for="item in menuList"
        :key="item.path"
        class="nav-item"
        :class="{ active: currentPath === item.path }"
        @click="handleMenuClick(item)"
      >
        <div class="nav-icon-wrapper">
          <el-icon :size="18"><component :is="item.icon" /></el-icon>
        </div>
        <span class="nav-text">{{ item.name }}</span>
        <div class="nav-active-indicator" v-if="currentPath === item.path"></div>
      </div>
    </div>

    <!-- 底部状态卡片 -->
    <div class="sidebar-footer">
      <div class="status-card">
        <div class="status-dot"></div>
        <div class="status-info">
          <div class="status-label">系统状态</div>
          <div class="status-value">运行正常</div>
        </div>
      </div>
      <div class="version">v2.0.1</div>
    </div>
  </div>
</template>

<script setup>
import { computed } from "vue";
import { useRouter, useRoute } from "vue-router";
import {
  Monitor,
  Picture,
  Clock,
  ChatDotRound,
  DataLine,
  User,
} from "@element-plus/icons-vue";

const router = useRouter();
const route = useRoute();

const menuList = [
  { name: "智能分类", icon: Picture, path: "/detection" },
  { name: "历史记录", icon: Clock, path: "/history" },
  { name: "AI 问答", icon: ChatDotRound, path: "/qa" },
  { name: "土地类型库", icon: DataLine, path: "/targets" },
  { name: "个人中心", icon: User, path: "/profile" },
];

const currentPath = computed(() => route.path);

const handleMenuClick = (item) => {
  router.push(item.path);
};
</script>

<style scoped>
.sidebar-container {
  height: 100%;
  display: flex;
  flex-direction: column;
  position: relative;
}

/* Logo */
.logo-section {
  height: 80px;
  display: flex;
  align-items: center;
  padding: 0 20px;
  border-bottom: 1px solid var(--border-color);
  position: relative;
  overflow: hidden;
}
.logo-glow {
  position: absolute;
  width: 100px;
  height: 100px;
  background: var(--accent-cyan);
  border-radius: 50%;
  filter: blur(40px);
  opacity: 0.15;
  top: 50%;
  left: 10px;
  transform: translateY(-50%);
}
.logo-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  background: var(--accent-gradient);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 12px;
  flex-shrink: 0;
  box-shadow: 0 4px 16px rgba(6, 182, 212, 0.3);
  position: relative;
  z-index: 1;
}
.logo-text {
  overflow: hidden;
  position: relative;
  z-index: 1;
}
.logo-title {
  font-size: 16px;
  font-weight: 700;
  color: var(--text-heading);
  line-height: 1.3;
  white-space: nowrap;
  letter-spacing: -0.02em;
}
.title-accent {
  background: var(--accent-gradient);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-left: 2px;
}
.logo-subtitle {
  font-size: 11px;
  color: var(--text-muted);
  margin-top: 2px;
  line-height: 1.3;
  white-space: nowrap;
  letter-spacing: 0.5px;
  text-transform: uppercase;
}

/* 导航菜单 */
.nav-menu {
  flex: 1;
  padding: 20px 14px;
  overflow-y: auto;
}
.menu-label {
  font-size: 10px;
  font-weight: 600;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 1.5px;
  margin: 0 8px 12px;
}

.nav-item {
  display: flex;
  align-items: center;
  padding: 13px 14px;
  border-radius: var(--border-radius-md);
  margin-bottom: 6px;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  text-align: left;
  position: relative;
  overflow: hidden;
}
.nav-item::before {
  content: '';
  position: absolute;
  inset: 0;
  background: var(--accent-gradient);
  opacity: 0;
  transition: opacity 0.3s;
}
.nav-item:hover {
  background: var(--bg-hover);
}
.nav-item:hover .nav-icon-wrapper {
  color: var(--accent-cyan);
}
.nav-item.active {
  background: rgba(6, 182, 212, 0.08);
}
.nav-item.active::before {
  opacity: 0.05;
}
.nav-item.active .nav-icon-wrapper {
  color: var(--accent-cyan);
  text-shadow: 0 0 12px rgba(6, 182, 212, 0.5);
}
.nav-item.active .nav-text {
  color: var(--text-heading);
  font-weight: 600;
}

.nav-icon-wrapper {
  margin-right: 12px;
  color: var(--text-muted);
  transition: all 0.3s;
  position: relative;
  z-index: 1;
  flex-shrink: 0;
}
.nav-text {
  font-size: 14px;
  color: var(--text-secondary);
  transition: all 0.3s;
  position: relative;
  z-index: 1;
}

.nav-active-indicator {
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 3px;
  height: 20px;
  background: var(--accent-gradient);
  border-radius: 0 3px 3px 0;
  box-shadow: 0 0 8px rgba(6, 182, 212, 0.5);
}

/* 底部状态 */
.sidebar-footer {
  padding: 16px;
  border-top: 1px solid var(--border-color);
}
.status-card {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px;
  background: rgba(16, 185, 129, 0.08);
  border: 1px solid rgba(16, 185, 129, 0.15);
  border-radius: var(--border-radius-md);
  margin-bottom: 10px;
}
.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--success);
  box-shadow: 0 0 8px rgba(16, 185, 129, 0.6);
  animation: pulse-dot 2s ease-in-out infinite;
}
@keyframes pulse-dot {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.6; transform: scale(1.2); }
}
.status-label {
  font-size: 11px;
  color: var(--text-muted);
}
.status-value {
  font-size: 12px;
  font-weight: 600;
  color: var(--success);
}
.version {
  text-align: center;
  font-size: 11px;
  color: var(--text-muted);
  letter-spacing: 0.5px;
}
</style>
