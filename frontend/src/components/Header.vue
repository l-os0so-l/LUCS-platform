<template>
  <div class="header-container">
    <div class="breadcrumbs">
      <div class="breadcrumb-glow">
        <el-icon class="breadcrumb-icon"><House /></el-icon>
      </div>
      <span class="breadcrumb-separator">/</span>
      <span class="breadcrumb-text">{{ pageTitle }}</span>
      <div class="live-indicator" v-if="isActivePage">
        <span class="live-dot"></span>
        <span class="live-text">实时</span>
      </div>
    </div>

    <div class="header-actions">
      <!-- 搜索框 -->
      <div class="header-search">
        <el-icon class="search-icon"><Search /></el-icon>
        <input type="text" placeholder="全局搜索..." class="search-input" />
      </div>

      <div class="action-icons">
        <div class="action-icon-wrapper" title="应用中心">
          <el-icon class="action-icon"><Grid /></el-icon>
        </div>
        <div class="action-icon-wrapper has-badge" title="消息通知">
          <el-icon class="action-icon"><Bell /></el-icon>
          <span class="badge">3</span>
        </div>
        <div class="action-icon-wrapper" title="帮助文档">
          <el-icon class="action-icon"><QuestionFilled /></el-icon>
        </div>

        <div class="divider"></div>

        <div class="user-dropdown">
          <div class="user-avatar-ring">
            <el-avatar class="user-avatar" size="34">
              <img
                src="https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png"
                alt="用户头像"
              />
            </el-avatar>
          </div>
          <div class="user-info">
            <div class="user-name">Lily</div>
            <div class="user-role">普通用户</div>
          </div>
          <el-icon class="dropdown-icon"><CaretBottom /></el-icon>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from "vue";
import { useRoute } from "vue-router";
import {
  Search,
  Grid,
  Bell,
  QuestionFilled,
  CaretBottom,
  House,
} from "@element-plus/icons-vue";

const route = useRoute();

const pageTitles = {
  "/detection": "智能分类",
  "/history": "历史记录",
  "/qa": "AI 问答",
  "/targets": "土地类型库",
  "/profile": "个人中心",
};

const pageTitle = computed(() => pageTitles[route.path] || "工作台");
const isActivePage = computed(() => route.path === "/detection");
</script>

<style scoped>
.header-container {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
}

.breadcrumbs {
  display: flex;
  align-items: center;
  gap: 8px;
}
.breadcrumb-glow {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  background: rgba(6, 182, 212, 0.1);
  border: 1px solid rgba(6, 182, 212, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s;
}
.breadcrumb-glow:hover {
  background: rgba(6, 182, 212, 0.2);
  box-shadow: 0 0 12px rgba(6, 182, 212, 0.2);
}
.breadcrumb-icon {
  font-size: 14px;
  color: var(--accent-cyan);
}
.breadcrumb-separator {
  font-size: 13px;
  color: var(--text-muted);
}
.breadcrumb-text {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-heading);
}

.live-indicator {
  display: flex;
  align-items: center;
  gap: 5px;
  margin-left: 10px;
  padding: 3px 10px;
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.2);
  border-radius: 20px;
}
.live-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--danger);
  animation: pulse-dot 2s ease-in-out infinite;
}
.live-text {
  font-size: 11px;
  font-weight: 500;
  color: var(--danger);
}

/* 搜索框 */
.header-search {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 14px;
  background: rgba(15, 23, 42, 0.6);
  border: 1px solid var(--border-color);
  border-radius: 20px;
  margin-right: 20px;
  transition: all 0.3s;
  width: 220px;
}
.header-search:hover,
.header-search:focus-within {
  border-color: var(--border-glow);
  box-shadow: 0 0 12px rgba(6, 182, 212, 0.1);
}
.search-icon {
  font-size: 14px;
  color: var(--text-muted);
}
.search-input {
  background: transparent;
  border: none;
  outline: none;
  color: var(--text-primary);
  font-size: 13px;
  width: 100%;
}
.search-input::placeholder {
  color: var(--text-muted);
}

.header-actions {
  display: flex;
  align-items: center;
}

.action-icons {
  display: flex;
  align-items: center;
  gap: 4px;
}

.action-icon-wrapper {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s;
  position: relative;
}
.action-icon-wrapper:hover {
  background: rgba(6, 182, 212, 0.1);
}
.action-icon-wrapper:hover .action-icon {
  color: var(--accent-cyan);
}
.action-icon {
  font-size: 18px;
  color: var(--text-muted);
  transition: all 0.3s;
}

.has-badge .badge {
  position: absolute;
  top: 2px;
  right: 2px;
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: var(--accent-gradient);
  color: white;
  font-size: 10px;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 8px rgba(236, 72, 153, 0.4);
}

.divider {
  width: 1px;
  height: 24px;
  background: var(--border-color);
  margin: 0 10px;
}

.user-dropdown {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  padding: 4px 10px;
  border-radius: 10px;
  transition: all 0.3s;
  margin-left: 4px;
}
.user-dropdown:hover {
  background: rgba(255, 255, 255, 0.05);
}

.user-avatar-ring {
  position: relative;
  padding: 2px;
  border-radius: 50%;
  background: var(--accent-gradient);
}
.user-avatar-ring::before {
  content: '';
  position: absolute;
  inset: -1px;
  border-radius: 50%;
  background: var(--accent-gradient);
  filter: blur(4px);
  opacity: 0.6;
}
.user-avatar {
  position: relative;
  border: 2px solid var(--bg-primary);
}

.user-info {
  line-height: 1.3;
}
.user-name {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-heading);
}
.user-role {
  font-size: 11px;
  color: var(--text-muted);
}

.dropdown-icon {
  font-size: 11px;
  color: var(--text-muted);
}
</style>
