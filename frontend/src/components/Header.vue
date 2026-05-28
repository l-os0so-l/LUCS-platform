<template>
  <div class="header-container">
    <div class="breadcrumbs">
      <div class="breadcrumb-glow" @click="goHome" title="返回智能分类">
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
      <div class="action-icons">
        <!-- 消息通知下拉 -->
        <el-dropdown trigger="click" popper-class="notification-dropdown">
          <div class="action-icon-wrapper has-badge" title="消息通知">
            <el-icon class="action-icon"><Bell /></el-icon>
            <span class="badge">3</span>
          </div>
          <template #dropdown>
            <el-dropdown-menu class="notification-menu">
              <div class="notification-header">
                <span>通知中心</span>
                <el-tag size="small" type="info">3 条未读</el-tag>
              </div>
              <el-dropdown-item v-for="(msg, i) in notifications" :key="i" class="notification-item">
                <div class="notification-dot" :class="{ unread: !msg.read }"></div>
                <div class="notification-content">
                  <div class="notification-title">{{ msg.title }}</div>
                  <div class="notification-time">{{ msg.time }}</div>
                </div>
              </el-dropdown-item>
              <div class="notification-footer">
                <span @click="clearNotifications">全部已读</span>
              </div>
            </el-dropdown-menu>
          </template>
        </el-dropdown>

        <!-- 项目简介 -->
        <div class="action-icon-wrapper" title="关于本项目" @click="showAbout = true">
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
            <div class="user-name">{{ currentUser.nickname || currentUser.username || '未登录' }}</div>
            <div class="user-role">{{ currentUser.role === 'admin' ? '管理员' : '普通用户' }}</div>
          </div>
          <el-icon class="dropdown-icon"><CaretBottom /></el-icon>
        </div>
      </div>
    </div>

    <!-- 项目简介弹窗 -->
    <el-dialog
      v-model="showAbout"
      title="关于 LUCS Platform"
      width="480px"
      align-center
      append-to-body
      class="about-dialog"
    >
      <div class="about-content">
        <div class="about-logo">
          <el-icon :size="40"><Monitor /></el-icon>
        </div>
        <h3 class="about-title">LUCS Platform</h3>
        <p class="about-subtitle">智能遥感分类系统</p>
        <div class="about-divider"></div>
        <div class="about-section">
          <h4>项目简介</h4>
          <p>本项目基于 DeepLabV3+ / ResNet50 语义分割模型，实现对遥感影像的 7 类土地类型智能分类，包括背景、建筑、道路、水域、裸地、林地、耕地。</p>
        </div>
        <div class="about-section">
          <h4>核心功能</h4>
          <ul>
            <li><strong>单图分类</strong>：快速上传单张遥感影像，获取像素级分割结果</li>
            <li><strong>批量分类</strong>：支持多图同时上传，批量推理</li>
            <li><strong>视频分类</strong>：实时帧检测，逐帧语义分割</li>
            <li><strong>历史记录</strong>：完整保存检测记录，支持查看与下载</li>
            <li><strong>AI 问答</strong>：土地利用分类知识智能问答</li>
          </ul>
        </div>
        <div class="about-section">
          <h4>技术栈</h4>
          <p>Vue 3 + Element Plus + FastAPI + PyTorch + DeepLabV3+</p>
        </div>
        <div class="about-version">版本 v2.0.1</div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, ref, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import {
  Bell,
  QuestionFilled,
  CaretBottom,
  House,
  Monitor,
} from "@element-plus/icons-vue";
import { getCurrentUser } from "../api/auth";

const route = useRoute();
const router = useRouter();

const currentUser = ref({
  username: "",
  nickname: "",
  role: "user",
});

onMounted(async () => {
  try {
    const res = await getCurrentUser();
    if (res.success && res.data) {
      currentUser.value = res.data;
    }
  } catch (e) {
    // 未登录或 token 过期，静默处理
  }
});

const pageTitles = {
  "/detection": "智能分类",
  "/history": "历史记录",
  "/qa": "AI 问答",
  "/targets": "土地类型库",
  "/profile": "个人中心",
};

const pageTitle = computed(() => pageTitles[route.path] || "工作台");
const isActivePage = computed(() => route.path === "/detection");

// 返回智能分类首页
const goHome = () => {
  router.push("/detection");
};

// 项目简介弹窗
const showAbout = ref(false);

// 消息通知数据
const notifications = ref([
  { title: "模型 land-seg-v1 加载成功", time: "10 分钟前", read: false },
  { title: "完成 Rural_4_1.png 分类任务", time: "30 分钟前", read: false },
  { title: "系统运行状态正常", time: "1 小时前", read: false },
]);

const clearNotifications = () => {
  notifications.value.forEach((n) => (n.read = true));
};
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
.breadcrumb-glow {
  cursor: pointer;
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

/* ── 通知下拉菜单 ── */
:deep(.notification-dropdown .el-dropdown-menu) {
  padding: 0;
  background: #1a1a2e;
  border: 1px solid var(--border-glow);
  border-radius: 12px;
  min-width: 280px;
}
.notification-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  border-bottom: 1px solid var(--border-color);
  font-size: 14px;
  font-weight: 600;
  color: var(--text-heading);
}
.notification-item {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  padding: 10px 16px;
  cursor: pointer;
}
.notification-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--text-muted);
  margin-top: 5px;
  flex-shrink: 0;
}
.notification-dot.unread {
  background: var(--accent-cyan);
  box-shadow: 0 0 6px rgba(6, 182, 212, 0.5);
}
.notification-content {
  flex: 1;
  line-height: 1.4;
}
.notification-title {
  font-size: 13px;
  color: var(--text-secondary);
}
.notification-time {
  font-size: 11px;
  color: var(--text-muted);
  margin-top: 2px;
}
.notification-footer {
  text-align: center;
  padding: 10px;
  border-top: 1px solid var(--border-color);
  font-size: 12px;
  color: var(--accent-cyan);
  cursor: pointer;
}
.notification-footer:hover {
  color: #22d3ee;
}

/* ── 关于弹窗 ── */
:deep(.about-dialog .el-dialog) {
  background: #1a1a2e;
  border: 1px solid var(--border-glow);
}
:deep(.about-dialog .el-dialog__title) {
  color: var(--text-heading);
}
.about-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 10px 0;
  text-align: center;
}
.about-logo {
  width: 64px;
  height: 64px;
  border-radius: 16px;
  background: var(--accent-gradient);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  margin-bottom: 14px;
  box-shadow: var(--accent-glow);
}
.about-title {
  font-size: 20px;
  font-weight: 700;
  color: var(--text-heading);
  margin: 0;
}
.about-subtitle {
  font-size: 13px;
  color: var(--text-muted);
  margin: 4px 0 16px;
}
.about-divider {
  width: 40px;
  height: 3px;
  background: var(--accent-gradient);
  border-radius: 2px;
  margin-bottom: 16px;
}
.about-section {
  width: 100%;
  text-align: left;
  margin-bottom: 14px;
}
.about-section h4 {
  font-size: 13px;
  font-weight: 600;
  color: var(--accent-cyan);
  margin: 0 0 6px;
}
.about-section p,
.about-section ul {
  font-size: 12px;
  color: var(--text-secondary);
  line-height: 1.7;
  margin: 0;
  padding-left: 16px;
}
.about-section ul {
  list-style: disc;
}
.about-section li {
  margin-bottom: 4px;
}
.about-version {
  font-size: 11px;
  color: var(--text-muted);
  margin-top: 8px;
}
</style>
