<template>
  <div class="history-page">
    <!-- 页面头部 -->
    <div class="page-header animate-fade-in-up">
      <div class="header-main">
        <h1 class="page-title">
          <span class="title-deco"></span>
          分类历史记录
        </h1>
        <p class="page-subtitle">查看和管理您的所有分类记录，追踪每一次智能分析</p>
      </div>
      <div class="header-stats">
        <div class="mini-stat">
          <div class="mini-stat-value">{{ totalRecords }}</div>
          <div class="mini-stat-label">总记录</div>
        </div>
      </div>
    </div>

    <!-- 搜索和筛选 -->
    <div class="search-bar animate-fade-in-up" style="animation-delay: 0.1s">
      <div class="search-input-wrap">
        <el-icon class="search-icon"><Search /></el-icon>
        <el-input
          v-model="searchQuery"
          placeholder="搜索文件名或ID..."
          size="default"
          class="search-input"
          @keyup.enter="fetchHistory"
        />
      </div>

      <button class="refresh-btn" @click="fetchHistory" title="刷新">
        <el-icon><Refresh /></el-icon>
      </button>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-state">
      <el-icon class="loading-spin" :size="32"><Loading /></el-icon>
      <span>加载中...</span>
    </div>

    <!-- 记录列表 -->
    <div v-else class="history-list">
      <div
        v-for="(record, index) in historyRecords"
        :key="record.detection_id"
        class="history-card glass-card animate-fade-in-up"
        :style="{ animationDelay: `${0.15 + index * 0.05}s` }"
        @click="viewRecord(record)"
      >
        <div class="card-accent-line completed"></div>

        <div class="record-preview">
          <img
            :src="getImageUrl(record.image_url)"
            :alt="record.filename"
            class="preview-image"
            @error="handleImageError"
          />
          <div class="status-badge completed">
            <el-icon><CircleCheck /></el-icon>
            完成
          </div>
        </div>

        <div class="record-info">
          <div class="record-header">
            <span class="record-filename">{{ record.filename }}</span>
            <span class="record-type">单图</span>
          </div>
          <div class="record-meta">
            <span class="meta-item">
              <el-icon><Clock /></el-icon>
              {{ formatTime(record.created_at) }}
            </span>
            <span class="meta-item">
              <el-icon><Aim /></el-icon>
              {{ record.inference_time.toFixed(2) }}s
            </span>
            <span class="meta-item">
              <el-icon><Cpu /></el-icon>
              {{ record.model_name }}
            </span>
          </div>
          <div class="record-tags">
            <span
              v-for="stat in record.class_stats.filter(s => s.pixel_ratio > 0.01)"
              :key="stat.class_id"
              class="detected-tag"
              :style="{ borderColor: stat.color_hex, color: stat.color_hex }"
            >
              {{ stat.class_name }} {{ (stat.pixel_ratio * 100).toFixed(1) }}%
            </span>
          </div>
        </div>

        <div class="record-actions">
          <button class="action-btn view" @click.stop="viewRecord(record)" title="查看详情">
            <el-icon><Monitor /></el-icon>
          </button>
          <button class="action-btn download" @click.stop="downloadOverlay(record)" title="下载叠加图">
            <el-icon><Download /></el-icon>
          </button>
          <button class="action-btn delete" @click.stop="deleteRecord(record)" title="删除记录">
            <el-icon><Delete /></el-icon>
          </button>
        </div>
      </div>
    </div>

    <!-- 空状态 -->
    <div v-if="!loading && historyRecords.length === 0" class="empty-state animate-fade-in-up">
      <div class="empty-illustration">
        <el-icon :size="56" class="empty-icon"><FolderOpened /></el-icon>
        <div class="empty-ring"></div>
      </div>
      <p class="empty-text">暂无分类记录</p>
      <p class="empty-desc">上传遥感影像，开始您的第一次智能分类</p>
      <button class="btn-primary glow-btn" @click="goToDetection">
        <el-icon><Plus /></el-icon>
        开始分类
      </button>
    </div>

    <!-- 分页 -->
    <div class="pagination-wrapper" v-if="totalRecords > pageSize">
      <el-pagination
        :total="totalRecords"
        :page-size="pageSize"
        :current-page="currentPage"
        @current-change="handlePageChange"
        layout="prev, pager, next"
      />
    </div>

    <!-- 详情弹窗 -->
    <el-dialog
      v-model="detailVisible"
      :title="detailRecord?.filename || '分类详情'"
      width="720px"
      class="detail-dialog"
      destroy-on-close
    >
      <div v-if="detailRecord" class="detail-content">
        <div class="detail-images">
          <div class="detail-img-block">
            <div class="detail-img-label">原始图像</div>
            <img :src="getImageUrl(detailRecord.image_url)" class="detail-img" />
          </div>
          <div class="detail-img-block">
            <div class="detail-img-label">分割结果</div>
            <img :src="getImageUrl(detailRecord.result_image_url)" class="detail-img" />
          </div>
          <div class="detail-img-block">
            <div class="detail-img-label">叠加效果</div>
            <img :src="getImageUrl(detailRecord.overlay_image_url)" class="detail-img" />
          </div>
        </div>

        <div class="detail-stats">
          <h4>分类统计</h4>
          <div class="stats-bar-chart">
            <div
              v-for="stat in detailRecord.class_stats"
              :key="stat.class_id"
              class="stat-bar-row"
            >
              <span class="stat-label" :style="{ color: stat.color_hex }">{{ stat.class_name }}</span>
              <div class="stat-bar-track">
                <div
                  class="stat-bar-fill"
                  :style="{ width: (stat.pixel_ratio * 100) + '%', background: stat.color_hex }"
                ></div>
              </div>
              <span class="stat-value">{{ (stat.pixel_ratio * 100).toFixed(1) }}%</span>
            </div>
          </div>
          <div class="detail-meta-row">
            <span>检测ID: {{ detailRecord.detection_id }}</span>
            <span>推理耗时: {{ detailRecord.inference_time.toFixed(2) }}s</span>
            <span>模型: {{ detailRecord.model_name }}</span>
            <span>时间: {{ formatTime(detailRecord.created_at) }}</span>
          </div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from "vue";
import { useRouter } from "vue-router";
import { ElMessage, ElMessageBox } from "element-plus";
import {
  Search, Clock, Aim, Monitor, Download, Delete,
  Plus, CircleCheck, Loading, Refresh, FolderOpened,
} from "@element-plus/icons-vue";
import {
  getDetectionHistory,
  getDetectionDetail,
  deleteDetectionHistory,
} from "@/api/detection";

const router = useRouter();

// ── 状态 ──────────────────────────────────────────────────
const loading = ref(false);
const historyRecords = ref([]);
const totalRecords = ref(0);
const currentPage = ref(1);
const pageSize = ref(10);
const searchQuery = ref("");

// 详情弹窗
const detailVisible = ref(false);
const detailRecord = ref(null);

// ── API 基地址 ────────────────────────────────────────────
const API_BASE = "http://localhost:8000";

const getImageUrl = (path) => {
  if (!path) return "";
  if (path.startsWith("http")) return path;
  return API_BASE + path;
};

// ── 格式化时间 ────────────────────────────────────────────
const formatTime = (dt) => {
  if (!dt) return "";
  const d = new Date(dt);
  const pad = (n) => String(n).padStart(2, "0");
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`;
};

// ── 获取历史记录 ──────────────────────────────────────────
const fetchHistory = async () => {
  loading.value = true;
  try {
    const res = await getDetectionHistory({
      page: currentPage.value,
      page_size: pageSize.value,
      search: searchQuery.value || undefined,
    });
    if (res.success) {
      historyRecords.value = res.data || [];
      totalRecords.value = res.total || 0;
    }
  } catch (e) {
    console.error("获取历史记录失败:", e);
    ElMessage.error("获取历史记录失败");
  } finally {
    loading.value = false;
  }
};

// ── 查看详情 ──────────────────────────────────────────────
const viewRecord = async (record) => {
  try {
    const res = await getDetectionDetail(record.detection_id);
    if (res.success) {
      detailRecord.value = res.data;
      detailVisible.value = true;
    }
  } catch (e) {
    // 如果详情接口失败，用列表中的数据回退
    detailRecord.value = record;
    detailVisible.value = true;
  }
};

// ── 下载叠加图 ────────────────────────────────────────────
const downloadOverlay = (record) => {
  const url = getImageUrl(record.overlay_image_url);
  if (!url) {
    ElMessage.warning("没有可下载的叠加图");
    return;
  }
  const a = document.createElement("a");
  a.href = url;
  a.download = record.filename?.replace(/\.\w+$/, "_overlay.png") || "overlay.png";
  a.target = "_blank";
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
};

// ── 删除记录 ──────────────────────────────────────────────
const deleteRecord = async (record) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除记录 "${record.filename}" 吗？此操作不可恢复。`,
      "确认删除",
      { confirmButtonText: "删除", cancelButtonText: "取消", type: "warning" }
    );
    const res = await deleteDetectionHistory(record.detection_id);
    if (res.success) {
      ElMessage.success("删除成功");
      fetchHistory();
    }
  } catch (e) {
    if (e !== "cancel") {
      console.error("删除失败:", e);
      ElMessage.error("删除失败");
    }
  }
};

// ── 图片加载失败 ──────────────────────────────────────────
const handleImageError = (e) => {
  e.target.src = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='120' height='80'%3E%3Crect fill='%231a1a2e' width='120' height='80'/%3E%3Ctext fill='%23555' x='50%25' y='50%25' text-anchor='middle' dy='.3em' font-size='12'%3EN/A%3C/text%3E%3C/svg%3E";
};

// ── 导航 ──────────────────────────────────────────────────
const goToDetection = () => router.push("/detection");
const handlePageChange = (page) => {
  currentPage.value = page;
  fetchHistory();
};

// ── 初始化 ────────────────────────────────────────────────
onMounted(() => {
  fetchHistory();
});
</script>

<style scoped>
.history-page {
  width: 100%;
}

.header-main {
  margin-bottom: 8px;
}
.title-deco {
  display: inline-block;
  width: 4px;
  height: 22px;
  background: var(--accent-gradient);
  border-radius: 2px;
  margin-right: 10px;
  vertical-align: middle;
}
.page-title {
  display: inline;
  vertical-align: middle;
}

.header-stats {
  display: flex;
  gap: 16px;
  margin-top: 12px;
}
.mini-stat {
  text-align: center;
  padding: 8px 16px;
  background: rgba(6, 182, 212, 0.08);
  border: 1px solid rgba(6, 182, 212, 0.15);
  border-radius: var(--border-radius-md);
}
.mini-stat-value {
  font-size: 18px;
  font-weight: 700;
  color: var(--accent-cyan);
}
.mini-stat-label {
  font-size: 11px;
  color: var(--text-muted);
  margin-top: 2px;
}

.search-bar {
  display: flex;
  gap: 12px;
  margin-bottom: 24px;
  align-items: center;
}
.search-input-wrap {
  flex: 1;
  max-width: 360px;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 0 12px;
  background: rgba(15, 23, 42, 0.6);
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius-md);
  transition: all 0.3s;
}
.search-input-wrap:hover,
.search-input-wrap:focus-within {
  border-color: var(--border-glow);
}
.search-icon {
  font-size: 14px;
  color: var(--text-muted);
}
:deep(.search-input .el-input__wrapper) {
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
}
.refresh-btn {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(15, 23, 42, 0.6);
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius-sm);
  color: var(--text-muted);
  cursor: pointer;
  transition: all 0.3s;
}
.refresh-btn:hover {
  border-color: var(--accent-cyan);
  color: var(--accent-cyan);
}

/* 加载状态 */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 60px 0;
  color: var(--text-muted);
}
.loading-spin {
  animation: spin 1s linear infinite;
}
@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.history-card {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 18px 20px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  transition: all 0.3s;
}
.history-card:hover {
  border-color: var(--border-glow);
  transform: translateX(4px);
}
.card-accent-line {
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 3px;
}
.card-accent-line.completed { background: var(--success); box-shadow: 0 0 8px rgba(16, 185, 129, 0.5); }

.record-preview {
  position: relative;
  width: 120px;
  height: 80px;
  border-radius: var(--border-radius-sm);
  overflow: hidden;
  flex-shrink: 0;
  border: 1px solid var(--border-color);
}
.preview-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.status-badge {
  position: absolute;
  bottom: 6px;
  left: 6px;
  padding: 3px 8px;
  border-radius: 10px;
  font-size: 11px;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 3px;
  backdrop-filter: blur(8px);
}
.status-badge.completed { background: rgba(16, 185, 129, 0.85); color: white; }

.record-info {
  flex: 1;
  min-width: 0;
}
.record-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 8px;
}
.record-filename {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-heading);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.record-type {
  padding: 2px 8px;
  background: rgba(99, 102, 241, 0.1);
  border: 1px solid rgba(99, 102, 241, 0.2);
  border-radius: 4px;
  font-size: 11px;
  color: var(--accent-purple);
  font-weight: 500;
  flex-shrink: 0;
}
.record-meta {
  display: flex;
  gap: 16px;
  margin-bottom: 8px;
}
.meta-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: var(--text-muted);
}
.record-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
}
.detected-tag {
  padding: 3px 8px;
  background: rgba(6, 182, 212, 0.08);
  border: 1px solid rgba(6, 182, 212, 0.15);
  color: var(--accent-cyan);
  border-radius: 4px;
  font-size: 11px;
}

.record-actions {
  display: flex;
  gap: 6px;
}
.action-btn {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(15, 23, 42, 0.6);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  color: var(--text-muted);
  cursor: pointer;
  transition: all 0.3s;
  font-size: 14px;
}
.action-btn:hover {
  transform: translateY(-2px);
}
.action-btn.view:hover { border-color: var(--accent-cyan); color: var(--accent-cyan); }
.action-btn.download:hover { border-color: var(--accent-purple); color: var(--accent-purple); }
.action-btn.delete:hover { border-color: var(--danger); color: var(--danger); }

.empty-illustration {
  position: relative;
  width: 80px;
  height: 80px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 16px;
}
.empty-icon {
  color: var(--text-muted);
  opacity: 0.4;
}
.empty-ring {
  position: absolute;
  inset: 0;
  border: 2px dashed rgba(99, 102, 241, 0.2);
  border-radius: 50%;
  animation: spin-slow 20s linear infinite;
}

.pagination-wrapper {
  display: flex;
  justify-content: center;
  margin-top: 32px;
}

/* ── 详情弹窗 ─────────────────────────────────────────── */
.detail-images {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
}
.detail-img-block {
  flex: 1;
  text-align: center;
}
.detail-img-label {
  font-size: 12px;
  color: var(--text-muted);
  margin-bottom: 6px;
}
.detail-img {
  width: 100%;
  border-radius: 8px;
  border: 1px solid var(--border-color);
}

.detail-stats h4 {
  margin: 0 0 12px;
  font-size: 14px;
  color: var(--text-heading);
}
.stats-bar-chart {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.stat-bar-row {
  display: flex;
  align-items: center;
  gap: 10px;
}
.stat-label {
  width: 50px;
  text-align: right;
  font-size: 12px;
  font-weight: 500;
}
.stat-bar-track {
  flex: 1;
  height: 14px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 7px;
  overflow: hidden;
}
.stat-bar-fill {
  height: 100%;
  border-radius: 7px;
  transition: width 0.5s ease;
  min-width: 2px;
}
.stat-value {
  width: 50px;
  font-size: 12px;
  color: var(--text-muted);
}
.detail-meta-row {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  margin-top: 16px;
  padding-top: 12px;
  border-top: 1px solid var(--border-color);
  font-size: 12px;
  color: var(--text-muted);
}

/* ── 暗色弹窗覆盖 ─────────────────────────────────────── */
:deep(.detail-dialog .el-dialog) {
  background: #1a1a2e;
  border: 1px solid var(--border-glow);
}
:deep(.detail-dialog .el-dialog__title) {
  color: var(--text-heading);
}
:deep(.detail-dialog .el-dialog__body) {
  color: var(--text-primary);
}
</style>
