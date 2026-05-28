<template>
  <div class="profile-page">
    <!-- 页面头部 -->
    <div class="page-header animate-fade-in-up">
      <h1 class="page-title">个人中心</h1>
      <p class="page-subtitle">管理你的账户信息和使用统计</p>
    </div>

    <div class="profile-content">
      <!-- 用户信息卡片 -->
      <div class="user-card glass-card animate-fade-in-up" style="animation-delay: 0.1s">
        <div class="user-bg-glow"></div>
        <div class="user-content">
          <div class="avatar-section">
            <div class="avatar-ring">
              <el-avatar size="90" class="user-avatar">
                <img src="https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png" alt="用户头像" />
              </el-avatar>
              <div class="avatar-status"></div>
            </div>
            <div class="user-basic-info">
              <div class="user-name">{{ user.nickname || user.username || '未登录' }}</div>
              <div class="user-role">
                <span class="role-badge">{{ user.role }}</span>
              </div>
              <div class="user-meta">
                <span><el-icon><Message /></el-icon> {{ user.email || '未设置邮箱' }}</span>
                <span><el-icon><Location /></el-icon> {{ user.location || '未设置位置' }}</span>
              </div>
            </div>
          </div>
          <div class="user-actions">
            <button class="btn-secondary" @click="saveProfile">
              <el-icon><Edit /></el-icon>
              保存资料
            </button>
            <button class="btn-primary glow-btn">
              <el-icon><Upload /></el-icon>
              更换头像
            </button>
          </div>
        </div>
      </div>

      <!-- 统计卡片 -->
      <div class="stats-row">
        <div
          v-for="(stat, index) in statsData"
          :key="stat.label"
          class="stat-card glass-card animate-fade-in-up"
          :style="{ animationDelay: `${0.15 + index * 0.05}s` }"
        >
          <div class="stat-glow" :class="stat.color"></div>
          <div class="stat-icon" :class="stat.color">
            <el-icon :size="24"><component :is="stat.icon" /></el-icon>
          </div>
          <div class="stat-value">{{ stat.value }}</div>
          <div class="stat-label">{{ stat.label }}</div>
          <div class="stat-trend" v-if="stat.trend">
            <el-icon><ArrowUp /></el-icon>
            {{ stat.trend }}
          </div>
        </div>
      </div>

      <!-- 账户设置 -->
      <div class="settings-card glass-card animate-fade-in-up" style="animation-delay: 0.35s">
        <div class="settings-header">
          <el-icon class="settings-icon"><Setting /></el-icon>
          <span>账户设置</span>
        </div>
        <div class="settings-list">
          <div class="setting-item">
            <div class="setting-info">
              <div class="setting-title">邮箱通知</div>
              <div class="setting-desc">接收分类完成、系统更新等邮件通知</div>
            </div>
            <el-switch v-model="settings.emailNotify" />
          </div>
          <div class="setting-item">
            <div class="setting-info">
              <div class="setting-title">自动保存结果</div>
              <div class="setting-desc">分类完成后自动保存到历史记录</div>
            </div>
            <el-switch v-model="settings.autoSave" active-color="#06b6d4" />
          </div>
          <div class="setting-item">
            <div class="setting-info">
              <div class="setting-title">深色模式</div>
              <div class="setting-desc">始终使用深色主题界面</div>
            </div>
            <el-switch v-model="settings.darkMode" active-color="#06b6d4" disabled />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { ElMessage } from "element-plus";
import {
  Picture, Aim, TrendCharts, Calendar, Edit, Upload,
  Message, Location, ArrowUp, Setting,
} from "@element-plus/icons-vue";
import { getUserProfile, getUserStats, updateUserProfile } from "../api/user";

const user = ref({
  username: "",
  nickname: "",
  email: "",
  role: "普通用户",
  avatar_url: "",
  location: "",
  created_at: "",
});

const statsData = ref([
  { value: "0", label: "总分类次数", icon: Picture, color: "cyan", trend: null },
  { value: "0", label: "累计模型类型", icon: Aim, color: "purple", trend: null },
  { value: "0s", label: "平均推理耗时", icon: TrendCharts, color: "green", trend: null },
  { value: "0", label: "使用天数", icon: Calendar, color: "pink", trend: null },
]);

const settings = ref({
  emailNotify: true,
  autoSave: true,
  darkMode: true,
});

const loading = ref(false);

const loadProfile = async () => {
  try {
    const profileRes = await getUserProfile();
    if (profileRes.success && profileRes.data) {
      const d = profileRes.data;
      user.value = {
        username: d.username || "",
        nickname: d.nickname || d.username || "",
        email: d.email || "",
        role: d.role === "admin" ? "管理员" : "普通用户",
        avatar_url: d.avatar_url || "",
        location: d.location || "",
        created_at: d.created_at || "",
      };
    }
  } catch (e) {
    console.error("加载用户信息失败", e);
  }
};

const loadStats = async () => {
  try {
    const statsRes = await getUserStats();
    if (statsRes.success && statsRes.data) {
      const d = statsRes.data;
      statsData.value = [
        { value: String(d.total_classifications || 0), label: "总分类次数", icon: Picture, color: "cyan", trend: null },
        { value: String(d.total_model_types || 0), label: "累计模型类型", icon: Aim, color: "purple", trend: null },
        { value: String(d.avg_inference_time || 0) + "s", label: "平均推理耗时", icon: TrendCharts, color: "green", trend: null },
        { value: String(d.usage_days || 0), label: "使用天数", icon: Calendar, color: "pink", trend: null },
      ];
    }
  } catch (e) {
    console.error("加载统计数据失败", e);
  }
};

const saveProfile = async () => {
  try {
    await updateUserProfile({
      nickname: user.value.nickname,
      email: user.value.email,
      location: user.value.location,
    });
    ElMessage.success("资料更新成功");
  } catch (e) {
    ElMessage.error("更新失败");
  }
};

onMounted(() => {
  loadProfile();
  loadStats();
});
</script>

<style scoped>
.profile-page {
  width: 100%;
  max-width: 900px;
}

.user-card {
  position: relative;
  overflow: hidden;
  margin-bottom: 24px;
  padding: 0;
}
.user-bg-glow {
  position: absolute;
  top: -100px;
  right: -100px;
  width: 300px;
  height: 300px;
  background: var(--accent-gradient);
  border-radius: 50%;
  filter: blur(80px);
  opacity: 0.1;
  pointer-events: none;
}
.user-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 28px;
  position: relative;
  z-index: 1;
}

.avatar-section {
  display: flex;
  align-items: center;
  gap: 20px;
}
.avatar-ring {
  position: relative;
  padding: 3px;
  border-radius: 50%;
  background: var(--accent-gradient);
}
:deep(.user-avatar) {
  border: 3px solid var(--bg-primary) !important;
}
.avatar-status {
  position: absolute;
  bottom: 4px;
  right: 4px;
  width: 14px;
  height: 14px;
  border-radius: 50%;
  background: var(--success);
  border: 2px solid var(--bg-primary);
  box-shadow: 0 0 8px rgba(16, 185, 129, 0.6);
}

.user-basic-info {
  line-height: 1.4;
}
.user-name {
  font-size: 22px;
  font-weight: 700;
  color: var(--text-heading);
  margin-bottom: 6px;
}
.role-badge {
  display: inline-block;
  padding: 3px 10px;
  background: rgba(6, 182, 212, 0.1);
  border: 1px solid rgba(6, 182, 212, 0.2);
  border-radius: 20px;
  font-size: 12px;
  color: var(--accent-cyan);
  font-weight: 500;
}
.user-meta {
  display: flex;
  gap: 16px;
  margin-top: 10px;
  font-size: 12px;
  color: var(--text-muted);
}
.user-meta span {
  display: flex;
  align-items: center;
  gap: 4px;
}

.user-actions {
  display: flex;
  gap: 10px;
}
.btn-secondary {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 18px;
  background: rgba(15, 23, 42, 0.6);
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius-md);
  color: var(--text-secondary);
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s;
}
.btn-secondary:hover {
  border-color: var(--border-glow);
  color: var(--accent-cyan);
}
.btn-primary {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 18px;
  font-size: 13px;
  font-weight: 600;
}

/* 统计卡片 */
.stats-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}
.stat-card {
  padding: 22px 18px;
  text-align: center;
  position: relative;
  overflow: hidden;
}
.stat-glow {
  position: absolute;
  top: -30px;
  right: -30px;
  width: 80px;
  height: 80px;
  border-radius: 50%;
  filter: blur(30px);
  opacity: 0.2;
  pointer-events: none;
}
.stat-glow.cyan { background: var(--accent-cyan); }
.stat-glow.purple { background: var(--accent-purple); }
.stat-glow.green { background: var(--success); }
.stat-glow.pink { background: var(--accent-pink); }

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 14px;
  color: white;
}
.stat-icon.cyan { background: linear-gradient(135deg, #06b6d4, #0891b2); box-shadow: 0 4px 16px rgba(6, 182, 212, 0.3); }
.stat-icon.purple { background: linear-gradient(135deg, #8b5cf6, #7c3aed); box-shadow: 0 4px 16px rgba(139, 92, 246, 0.3); }
.stat-icon.green { background: linear-gradient(135deg, #10b981, #059669); box-shadow: 0 4px 16px rgba(16, 185, 129, 0.3); }
.stat-icon.pink { background: linear-gradient(135deg, #ec4899, #db2777); box-shadow: 0 4px 16px rgba(236, 72, 153, 0.3); }

.stat-value {
  font-size: 26px;
  font-weight: 700;
  color: var(--text-heading);
  margin-bottom: 4px;
}
.stat-label {
  font-size: 12px;
  color: var(--text-muted);
  margin-bottom: 6px;
}
.stat-trend {
  display: inline-flex;
  align-items: center;
  gap: 2px;
  padding: 2px 8px;
  background: rgba(16, 185, 129, 0.1);
  border-radius: 10px;
  font-size: 11px;
  color: var(--success);
  font-weight: 500;
}

/* 设置卡片 */
.settings-card {
  padding: 24px;
}
.settings-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 20px;
  font-size: 15px;
  font-weight: 600;
  color: var(--text-heading);
}
.settings-icon {
  font-size: 18px;
  color: var(--accent-cyan);
}
.settings-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.setting-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border-radius: var(--border-radius-md);
  transition: all 0.3s;
}
.setting-item:hover {
  background: rgba(255, 255, 255, 0.02);
}
.setting-title {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-heading);
  margin-bottom: 4px;
}
.setting-desc {
  font-size: 12px;
  color: var(--text-muted);
}

@media (max-width: 768px) {
  .stats-row {
    grid-template-columns: repeat(2, 1fr);
  }
  .user-content {
    flex-direction: column;
    gap: 20px;
    align-items: flex-start;
  }
}
</style>
