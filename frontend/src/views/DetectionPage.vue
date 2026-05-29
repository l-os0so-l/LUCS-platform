<template>
  <div class="detection-page">
    <!-- 页面头部 -->
    <div class="page-header animate-fade-in-up">
      <div class="header-content">
        <div class="breadcrumb">
          <span class="breadcrumb-item">工作台</span>
          <span class="breadcrumb-separator">
            <el-icon><ArrowRight /></el-icon>
          </span>
          <span class="breadcrumb-item active">智能分类</span>
        </div>
        <h1 class="page-title">
          <span class="title-icon">
            <el-icon><Picture /></el-icon>
          </span>
          上传遥感影像，智能分类土地类型
        </h1>
        <p class="page-subtitle">支持耕地、林地、水域、建筑等多类型土地智能识别与分割</p>
      </div>

      <div class="model-selector glass-card">
        <el-icon class="selector-icon"><SetUp /></el-icon>
        <el-select v-model="selectedModel" style="width: 160px">
          <el-option label="land-seg-v1" value="land-seg-v1" />
        </el-select>
      </div>
    </div>

    <!-- 功能选项卡 -->
    <div class="function-tabs animate-fade-in-up" style="animation-delay: 0.15s">
      <div
        v-for="(tab, index) in functionTabs"
        :key="tab.key"
        class="function-tab glass-card"
        :class="{ active: activeTab === tab.key }"
        :data-key="tab.key"
        @click="handleTabClick(tab.key)"
        :style="{ animationDelay: `${0.2 + index * 0.05}s` }"
      >
        <input
          type="file"
          :accept="tab.accept"
          :multiple="tab.multiple"
          :webkitdirectory="tab.key === 'folder' || undefined"
          :directory="tab.key === 'folder' || undefined"
          class="file-input"
          @change="handleFileChange($event, tab.key)"
          @click.stop="activateTab(tab.key)"
          ref="fileInputs"
        />
        <div class="tab-icon-wrap" :class="tab.key">
          <el-icon :size="22"><component :is="tab.icon" /></el-icon>
        </div>
        <div class="tab-content">
          <span class="tab-text">{{ tab.name }}</span>
          <span class="tab-desc">{{ tab.desc }}</span>
        </div>
        <div class="tab-glow" v-if="activeTab === tab.key"></div>
      </div>
    </div>

    <!-- 批量进度条 -->
    <div v-if="batchMode && batchTotal > 0" class="batch-progress-bar glass-card animate-fade-in-up">
      <div class="batch-progress-header">
        <span>批量分类进度</span>
        <span>{{ batchDone }} / {{ batchTotal }}</span>
      </div>
      <div class="batch-progress-track">
        <div class="batch-progress-fill" :style="{ width: batchProgress + '%' }"></div>
      </div>
      <div v-if="batchErrors.length" class="batch-errors">
        <span v-for="(e, i) in batchErrors" :key="i" class="batch-error-item">
          <el-icon><CircleClose /></el-icon>{{ e }}
        </span>
      </div>
    </div>

    <!-- 主内容区域 -->
    <div class="main-content animate-fade-in-up" style="animation-delay: 0.25s">
      <!-- ========== 视频检测模式 ========== -->
      <template v-if="activeTab === 'video'">
        <!-- 左侧视频面板 -->
        <div class="left-panel glass-card video-panel">
          <div class="panel-header">
            <div class="panel-title-wrap">
              <el-icon class="panel-icon"><Monitor /></el-icon>
              <span class="panel-title">视频分类</span>
            </div>
            <div class="panel-tags">
              <span class="tech-badge" v-if="isRealtimeDetecting">
                <el-icon><Loading /></el-icon>
                实时检测中
              </span>
              <span class="tech-badge wait-badge" v-else-if="videoUrl">
                <el-icon><VideoPlay /></el-icon>
                准备就绪
              </span>
              <span class="tech-badge wait-badge" v-else>
                <el-icon><Loading /></el-icon>
                等待上传
              </span>
            </div>
          </div>

          <!-- 未上传：占位提示 -->
          <div v-if="!videoUrl" class="video-placeholder" @click="handleTabClick('video')">
            <el-icon class="placeholder-icon" :size="48"><Monitor /></el-icon>
            <p class="placeholder-text">点击上传视频</p>
            <p class="placeholder-desc">支持 mp4、avi、mov 等格式</p>
          </div>

          <!-- 已上传：左右对比布局 -->
          <template v-else>
            <!-- 工具栏 -->
            <div class="toolbar">
              <button
                :class="['tool-btn', { active: videoShowMode === 'overlay' }]"
                @click="videoShowMode = 'overlay'"
              >
                <el-icon><View /></el-icon>
                叠加图
              </button>
              <button
                :class="['tool-btn', { active: videoShowMode === 'side' }]"
                @click="videoShowMode = 'side'"
              >
                <el-icon><CopyDocument /></el-icon>
                原图+分割
              </button>
            </div>

            <!-- 左右对比 -->
            <div class="video-compare-wrap">
              <!-- 左侧：原视频 -->
              <div class="video-compare-card">
                <div class="video-player-wrap">
                  <video
                    ref="videoRef"
                    :src="videoUrl"
                    class="video-player"
                    controls
                    @ended="stopRealtimeDetection"
                  />
                </div>
                <div class="image-label">原始视频</div>
              </div>

              <!-- 右侧：检测结果 -->
              <div class="video-compare-card">
                <div v-if="!videoFrameResult" class="empty-state-mini" style="height:100%; justify-content:center;">
                  <div class="empty-orb">
                    <el-icon><CircleCheck /></el-icon>
                  </div>
                  <p class="empty-text">等待检测</p>
                  <p class="empty-desc">开始实时检测后，分割结果将显示在这里</p>
                </div>
                <template v-else>
                  <img
                    v-if="videoShowMode === 'overlay'"
                    :src="videoFrameOverlay"
                    alt="实时叠加图"
                    class="video-result-img"
                  />
                  <img
                    v-else
                    :src="videoFrameMask"
                    alt="实时分割图"
                    class="video-result-img"
                  />
                  <div class="image-label">
                    {{ videoShowMode === 'overlay'
                      ? `实时叠加图（第 ${currentFrameIndex} 帧）`
                      : '分割结果' }}
                  </div>
                </template>
              </div>
            </div>
          </template>
        </div>

        <!-- 右侧视频设置面板 -->
        <div class="right-panel">
          <!-- 检测设置 -->
          <div class="info-card glass-card collapsible-card">
            <div class="card-title-small collapsible-header" @click="settingsCollapsed = !settingsCollapsed">
              <span class="header-left">
                <el-icon><SetUp /></el-icon>
                检测设置
              </span>
              <el-icon class="collapse-arrow" :class="{ rotated: !settingsCollapsed }"><ArrowRight /></el-icon>
            </div>
            <div v-show="!settingsCollapsed" class="collapsible-body">
              <div class="info-item">
                <span class="info-label">检测模式</span>
                <span class="info-value highlight">实时帧检测</span>
              </div>
              <div class="info-item">
                <span class="info-label">分类模型</span>
                <span class="info-value">{{ selectedModel }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">模型架构</span>
                <span class="info-value">DeepLabV3+ / ResNet50</span>
              </div>
            </div>
          </div>

          <!-- 帧率设置 -->
          <div class="result-card glass-card collapsible-card">
            <div class="card-title-small collapsible-header" @click="fpsCollapsed = !fpsCollapsed">
              <span class="header-left">
                <el-icon><Timer /></el-icon>
                检测帧率
              </span>
              <el-icon class="collapse-arrow" :class="{ rotated: !fpsCollapsed }"><ArrowRight /></el-icon>
            </div>
            <div v-show="!fpsCollapsed" class="collapsible-body">
              <div class="param-item">
                <div class="param-label">
                  <span>每秒检测 {{ detectionFPS }} 帧</span>
                </div>
                <el-slider v-model="detectionFPS" :min="1" :max="10" :step="1" :disabled="isRealtimeDetecting" />
                <div class="param-tip">越高检测越频繁，但可能增加延迟</div>
              </div>
            </div>
          </div>

          <!-- 实时像素统计 -->
          <div class="result-card glass-card">
            <div class="card-title-small">
              <el-icon><Histogram /></el-icon>
              当前帧像素统计
            </div>
            <div v-if="!videoFrameResult" class="empty-state-mini">
              <div class="empty-orb">
                <el-icon><CircleCheck /></el-icon>
              </div>
              <p class="empty-text">未识别到类型</p>
              <p class="empty-desc">开始检测后显示当前帧统计</p>
            </div>
            <div v-else class="stats-list">
              <div
                v-for="stat in sortedVideoStats"
                :key="stat.class_id"
                class="stat-row"
              >
                <div class="stat-bar-wrapper">
                  <div
                    class="stat-bar"
                    :style="{ width: (stat.pixel_ratio * 100).toFixed(1) + '%', background: `linear-gradient(90deg, ${stat.color_hex}, ${stat.color_hex}aa)` }"
                  ></div>
                </div>
                <div class="stat-info">
                  <span class="stat-name">{{ stat.class_name }}</span>
                  <span class="stat-ratio">{{ (stat.pixel_ratio * 100).toFixed(1) }}%</span>
                </div>
              </div>
            </div>
          </div>

          <!-- 操作按钮 -->
          <div class="action-buttons">
            <button class="btn-secondary" @click="handleTabClick('video')">
              <el-icon><Upload /></el-icon>
              更换视频
            </button>
            <button
              v-if="!isRealtimeDetecting"
              class="btn-primary glow-btn"
              :disabled="!videoUrl"
              @click="startRealtimeDetection"
            >
              <el-icon><VideoPlay /></el-icon>
              开始检测
            </button>
            <button
              v-else
              class="btn-primary glow-btn"
              style="background: linear-gradient(135deg, #ef4444, #dc2626);"
              @click="stopRealtimeDetection"
            >
              <el-icon><VideoPause /></el-icon>
              停止检测
            </button>
          </div>
        </div>
      </template>

      <!-- ========== 图片检测模式 ========== -->
      <template v-else>
      <!-- 左侧分类结果区域 -->
      <div class="left-panel glass-card">
        <div class="panel-header">
          <div class="panel-title-wrap">
            <el-icon class="panel-icon"><View /></el-icon>
            <span class="panel-title">分类预览</span>
          </div>
          <div class="panel-tags">
            <span class="tech-badge" v-if="detectionResult">
              <el-icon><Check /></el-icon>
              分类完成
            </span>
            <span class="tech-badge wait-badge" v-else>
              <el-icon><Loading /></el-icon>
              等待分类
            </span>
          </div>
        </div>

        <!-- 三图对比展示 -->
        <div class="image-compare grid">
          <div class="image-card">
            <img :src="originalImage || 'https://images.unsplash.com/photo-1500382017468-9049fed747ef?w=400&h=300&fit=crop'" alt="原始图片" class="compare-image" />
            <div class="image-label">原始图片</div>
          </div>
          <div class="image-card">
            <img :src="resultImage || 'https://images.unsplash.com/photo-1500382017468-9049fed747ef?w=400&h=300&fit=crop'" alt="分割结果" class="compare-image" />
            <div class="image-label">分割结果</div>
          </div>
          <div class="image-card">
            <img :src="overlayImage || 'https://images.unsplash.com/photo-1500382017468-9049fed747ef?w=400&h=300&fit=crop'" alt="叠加图" class="compare-image" />
            <div class="image-label">叠加图</div>
          </div>
        </div>

        <!-- 批量缩略图条 -->
        <div v-if="batchMode && batchResults.length > 1" class="batch-thumbnail-strip">
          <div
            v-for="(item, index) in batchResults"
            :key="index"
            class="batch-thumb"
            :class="{ active: batchCurrentIndex === index }"
            @click="selectBatchResult(index)"
          >
            <img :src="item.originalUrl" :alt="item.fileName" />
            <span class="thumb-label" :title="item.fileName">{{ item.fileName }}</span>
          </div>
        </div>

        <!-- AI 诊断建议 -->
        <div class="result-card diagnosis-card" style="margin-top: 12px;">
          <div class="card-title-small">
            <el-icon><ChatDotRound /></el-icon>
            AI 诊断建议
          </div>
          <div class="diagnosis-content">
            <div class="diagnosis-avatar">
              <el-icon><MagicStick /></el-icon>
            </div>
            <p v-if="!detectionResult" class="diagnosis-placeholder">未识别到指定类型，请上传影像获取AI分析</p>
            <div v-else>
              <p class="diagnosis-text">
                影像总像素 <strong>{{ detectionResult.total_pixels.toLocaleString() }}</strong>，
                推理耗时 <strong>{{ detectionResult.inference_time }}s</strong>。
                主要土地类型为 <span class="highlight-text">{{ dominantClass }}</span>，
                占比 <strong>{{ dominantRatio }}%</strong>。
              </p>
              <p v-if="forestRatio > 20" class="advice-tip">
                🌲 森林覆盖率较高，生态环境良好。
              </p>
              <p v-if="buildingRatio > 30" class="advice-tip">
                🏙️ 建筑用地占比较高，城镇化程度较强。
              </p>
              <p v-if="agriRatio > 40" class="advice-tip">
                🌾 耕地资源丰富，农业发展潜力大。
              </p>
              <p v-if="waterRatio > 15" class="advice-tip">
                💧 水域面积可观，注意水资源保护。
              </p>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧信息面板 -->
      <div class="right-panel">
        <!-- 模型信息 -->
        <div class="info-card glass-card">
          <div class="card-title-small info-header" @click="toggleModelInfo">
            <el-icon><Cpu /></el-icon>
            <span>模型信息</span>
            <div class="toggle-indicator">
              <el-icon :size="16">
                <component :is="modelInfoCollapsed ? Plus : Minus" />
              </el-icon>
            </div>
          </div>
          <div v-show="!modelInfoCollapsed" class="info-details">
            <div class="info-item">
              <span class="info-label">分类模型</span>
              <span class="info-value highlight">{{ selectedModel }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">模型架构</span>
              <span class="info-value">DeepLabV3+ / ResNet50</span>
            </div>
            <div class="info-item">
              <span class="info-label">输入尺寸</span>
              <span class="info-value">512 × 512</span>
            </div>
          </div>
        </div>

        <!-- 类别像素统计 -->
        <div class="result-card glass-card">
          <div class="card-title-small">
            <el-icon><Histogram /></el-icon>
            像素统计
          </div>
          <div v-if="!detectionResult" class="empty-state-mini">
            <div class="empty-orb">
              <el-icon><CircleCheck /></el-icon>
            </div>
            <p class="empty-text">未识别到类型</p>
            <p class="empty-desc">请先上传遥感影像</p>
          </div>
          <div v-else class="stats-list">
            <div
              v-for="stat in sortedStats"
              :key="stat.class_id"
              class="stat-row"
            >
              <div class="stat-bar-wrapper">
                <div
                  class="stat-bar"
                  :style="{ width: (stat.pixel_ratio * 100).toFixed(1) + '%', background: `linear-gradient(90deg, ${stat.color_hex}, ${stat.color_hex}aa)` }"
                ></div>
              </div>
              <div class="stat-info">
                <span class="stat-name">{{ stat.class_name }}</span>
                <span class="stat-ratio">{{ (stat.pixel_ratio * 100).toFixed(1) }}%</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 操作按钮 -->
        <div class="action-buttons">
          <button class="btn-secondary" @click="handleRedetect">
            <el-icon><Refresh /></el-icon>
            重新分类
          </button>
          <button class="btn-primary glow-btn">
            <el-icon><Document /></el-icon>
            查看完整报告
          </button>
        </div>
      </div>
      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onUnmounted, nextTick } from "vue";
import { ElMessage, ElLoading } from "element-plus";
import {
  Picture, Plus, Folder, Monitor, Check, Grid, View,
  CircleCheck, CircleClose, ChatDotRound, Refresh, Minus, Loading,
  ArrowRight, SetUp, Aim, TrendCharts, Timer, CopyDocument,
  Histogram, Cpu, MagicStick, Document, VideoPlay, VideoPause, Upload,
} from "@element-plus/icons-vue";
import { detectSingleImage, detectVideoFrame } from "../api/detection";

const selectedModel = ref("land-seg-v1");
const activeTab = ref("");
const showMode = ref("side");
const originalImage = ref("");
const resultImage = ref("");
const overlayImage = ref("");
const detectionResult = ref(null);
const isDetecting = ref(false);
const modelInfoCollapsed = ref(true);

// 批量模式状态
const batchMode = ref(false);
const batchTotal = ref(0);
const batchDone = ref(0);
const batchErrors = ref([]);
const batchResults = ref([]);
const batchCurrentIndex = ref(0);

// ─── 视频检测状态 ───
const videoMode = ref(false);           // 是否处于视频检测模式
const videoFile = ref(null);            // 视频文件对象
const videoUrl = ref("");               // 视频本地预览 URL
const videoRef = ref(null);             // video 元素引用
const isRealtimeDetecting = ref(false); // 实时检测中
const videoFrameResult = ref(null);     // 当前帧分割结果
const videoFrameOverlay = ref("");      // 当前帧叠加图 base64
const videoFrameMask = ref("");         // 当前帧分割图 base64
const currentFrameIndex = ref(0);       // 当前帧序号
const detectionFPS = ref(3);            // 检测帧率（fps）
const videoShowMode = ref("overlay");   // 视频结果展示模式: overlay / side
const settingsCollapsed = ref(true);    // 检测设置默认折叠
const fpsCollapsed = ref(true);         // 检测帧率默认折叠
let detectionTimer = null;              // 检测定时器
let isProcessingFrame = false;          // 防止同时处理多帧

const batchProgress = computed(() =>
  batchTotal.value > 0 ? Math.round((batchDone.value / batchTotal.value) * 100) : 0
);

const sortedStats = computed(() => {
  if (!detectionResult.value) return [];
  return [...detectionResult.value.class_stats].sort((a, b) => b.pixel_ratio - a.pixel_ratio);
});

const dominantClass = computed(() => {
  if (!detectionResult.value) return "";
  const nonBg = detectionResult.value.class_stats.filter(s => s.class_id !== 0);
  if (nonBg.length === 0) return "背景";
  const top = nonBg.reduce((a, b) => a.pixel_ratio > b.pixel_ratio ? a : b);
  return top.class_name;
});

const dominantRatio = computed(() => {
  if (!detectionResult.value) return "0";
  const nonBg = detectionResult.value.class_stats.filter(s => s.class_id !== 0);
  if (nonBg.length === 0) return "0";
  const top = nonBg.reduce((a, b) => a.pixel_ratio > b.pixel_ratio ? a : b);
  return (top.pixel_ratio * 100).toFixed(1);
});

const sortedVideoStats = computed(() => {
  if (!videoFrameResult.value) return [];
  return [...videoFrameResult.value.class_stats].sort((a, b) => b.pixel_ratio - a.pixel_ratio);
});

// 各类别占比（用于建议）
const getStatRatio = (classId) => {
  if (!detectionResult.value) return 0;
  const s = detectionResult.value.class_stats.find(x => x.class_id === classId);
  return s ? s.pixel_ratio * 100 : 0;
};
const forestRatio = computed(() => getStatRatio(6));
const buildingRatio = computed(() => getStatRatio(2));
const agriRatio = computed(() => getStatRatio(5));
const waterRatio = computed(() => getStatRatio(4));

// 批量结果切换
const selectBatchResult = (index) => {
  batchCurrentIndex.value = index;
  const item = batchResults.value[index];
  originalImage.value = item.originalUrl;
  detectionResult.value = item.data;
  resultImage.value = item.resultUrl;
  overlayImage.value = item.overlayUrl;
};

const functionTabs = [
  { key: "single", name: "单图分类", desc: "快速分类一张图片", icon: Picture, accept: "image/*", multiple: false },
  { key: "batch", name: "批量分类", desc: "一次处理多张图片", icon: Plus, accept: "image/*", multiple: true },
  { key: "folder", name: "文件夹", desc: "上传整个文件夹", icon: Folder, accept: "image/*", multiple: true },
  { key: "video", name: "视频分类", desc: "上传视频自动分类", icon: Monitor, accept: "video/*", multiple: false },
];

const toggleModelInfo = () => {
  modelInfoCollapsed.value = !modelInfoCollapsed.value;
};

const resetDetectionState = () => {
  detectionResult.value = null;
  originalImage.value = "";
  resultImage.value = "";
  overlayImage.value = "";
};

const activateTab = (key) => {
  activeTab.value = key;
  resetBatchState();
  resetDetectionState();
};

const fileInputs = ref([]);

const handleTabClick = (key) => {
  activateTab(key);
  const input = document.querySelector(`.function-tab[data-key="${key}"] .file-input`);
  if (input) input.click();
};

const handleFileChange = async (event, tabKey) => {
  event.stopPropagation();
  event.preventDefault();
  const files = Array.from(event.target.files || []);
  if (!files.length) return;

  if (tabKey === "single") {
    batchMode.value = false;
    await performSingleDetection(files[0]);
  } else if (tabKey === "batch" || tabKey === "folder") {
    const imageFiles = files.filter(f => f.type.startsWith("image/"));
    if (!imageFiles.length) {
      ElMessage.warning("未找到有效的图片文件");
      return;
    }
    await performBatchDetection(imageFiles);
  } else if (tabKey === "video") {
    await handleVideoUpload(files[0]);
  }

  setTimeout(() => { event.target.value = ''; }, 0);
};

const performSingleDetection = async (file) => {
  const loading = ElLoading.service({
    lock: true,
    text: "AI 正在分析影像...",
    background: "rgba(6, 11, 20, 0.85)",
  });
  try {
    isDetecting.value = true;
    const formData = new FormData();
    formData.append("file", file);
    formData.append("model_name", selectedModel.value);
    originalImage.value = URL.createObjectURL(file);
    const response = await detectSingleImage(formData);
    if (response.success && response.data) {
      detectionResult.value = response.data;
      resultImage.value = "http://localhost:8000" + response.data.result_image_url;
      overlayImage.value = "http://localhost:8000" + response.data.overlay_image_url;
      ElMessage.success("分类成功！");
    } else {
      ElMessage.error(response.message || "分类失败");
    }
  } catch (error) {
    ElMessage.error("分类失败，请稍后重试");
  } finally {
    isDetecting.value = false;
    loading.close();
  }
};

// 批量分类
const performBatchDetection = async (files) => {
  batchMode.value = true;
  batchTotal.value = files.length;
  batchDone.value = 0;
  batchErrors.value = [];
  batchResults.value = [];
  batchCurrentIndex.value = 0;

  ElMessage.info(`开始批量分类，共 ${files.length} 张图片`);

  for (const file of files) {
    try {
      const formData = new FormData();
      formData.append("file", file);
      formData.append("model_name", selectedModel.value);

      const response = await detectSingleImage(formData);
      console.log('API response:', file.name, response);
      if (response.success && response.data) {
        const item = {
          fileName: file.name,
          originalUrl: URL.createObjectURL(file),
          data: response.data,
          resultUrl: "http://localhost:8000" + response.data.result_image_url,
          overlayUrl: "http://localhost:8000" + response.data.overlay_image_url,
        };
        batchResults.value.push(item);

        // 每张完成后立即显示结果
        const idx = batchResults.value.length - 1;
        selectBatchResult(idx);
      } else {
        batchErrors.value.push(file.name);
      }
    } catch (error) {
      const detail = error.response?.data?.detail || error.message || '未知错误';
      console.error('Upload failed:', file.name, detail);
      batchErrors.value.push(file.name);
    } finally {
      batchDone.value++;
    }
  }

  if (batchErrors.value.length === 0) {
    ElMessage.success(`批量分类完成！共处理 ${files.length} 张，已保存至历史记录`);
  } else {
    ElMessage.warning(`批量分类完成，${batchErrors.value.length} 张失败`);
  }
};

// ─── 视频检测方法 ───

const handleVideoUpload = async (file) => {
  if (!file.type.startsWith("video/")) {
    ElMessage.warning("请选择有效的视频文件");
    return;
  }
  batchMode.value = false;
  batchTotal.value = 0;
  batchDone.value = 0;
  if (videoUrl.value) {
    URL.revokeObjectURL(videoUrl.value);
  }
  videoFile.value = file;
  videoUrl.value = URL.createObjectURL(file);
  videoMode.value = true;
  videoFrameResult.value = null;
  videoFrameOverlay.value = "";
  videoFrameMask.value = "";
  currentFrameIndex.value = 0;
  isRealtimeDetecting.value = false;
  ElMessage.success("视频加载成功，点击开始检测");
};

const startRealtimeDetection = async () => {
  batchMode.value = false;
  batchTotal.value = 0;
  batchDone.value = 0;
  const video = videoRef.value;
  if (!video) {
    ElMessage.error("视频未加载");
    return;
  }
  if (video.readyState < 2) {
    ElMessage.info("正在加载视频，请稍候...");
    await new Promise((resolve) => {
      video.onloadeddata = resolve;
      video.onerror = () => {
        ElMessage.error("视频加载失败");
        resolve();
      };
      setTimeout(resolve, 10000);
    });
  }
  if (video.readyState < 2) {
    ElMessage.error("视频加载失败");
    return;
  }

  isRealtimeDetecting.value = true;
  currentFrameIndex.value = 0;
  videoFrameResult.value = null;
  isProcessingFrame = false;

  try {
    await video.play();
    ElMessage.success("开始实时检测");
  } catch (err) {
    console.error("播放失败:", err);
    ElMessage.warning("自动播放被阻止，请手动点击播放");
  }

  const intervalMs = Math.floor(1000 / detectionFPS.value);
  detectionTimer = setInterval(captureAndDetectFrame, intervalMs);
};

const stopRealtimeDetection = () => {
  const video = videoRef.value;
  if (detectionTimer) {
    clearInterval(detectionTimer);
    detectionTimer = null;
  }
  if (video) {
    video.pause();
  }
  isRealtimeDetecting.value = false;
  isProcessingFrame = false;
};

const captureAndDetectFrame = async () => {
  const video = videoRef.value;
  if (!video || video.paused || video.ended || isProcessingFrame) return;

  isProcessingFrame = true;
  try {
    // 创建临时 Canvas 捕获当前帧
    const tempCanvas = document.createElement("canvas");
    tempCanvas.width = video.videoWidth;
    tempCanvas.height = video.videoHeight;
    const ctx = tempCanvas.getContext("2d");
    ctx.drawImage(video, 0, 0);

    // 压缩为 JPEG 以加速传输
    const blob = await new Promise((resolve) => {
      tempCanvas.toBlob((b) => resolve(b), "image/jpeg", 0.6);
    });

    if (!blob) {
      isProcessingFrame = false;
      return;
    }

    const formData = new FormData();
    formData.append("file", blob, "frame.jpg");
    formData.append("model_name", selectedModel.value);

    const response = await detectVideoFrame(formData);

    if (response.success && response.data) {
      videoFrameResult.value = response.data;
      videoFrameMask.value = "data:image/png;base64," + response.data.mask_base64;
      videoFrameOverlay.value = "data:image/png;base64," + response.data.overlay_base64;
      currentFrameIndex.value++;
    }
  } catch (error) {
    console.error("帧检测失败:", error);
  } finally {
    isProcessingFrame = false;
  }
};

const handleRedetect = () => {
  const key = activeTab.value === "batch" || activeTab.value === "folder" ? activeTab.value : "single";
  const input = document.querySelector(`.function-tab[data-key="${key}"] .file-input`);
  if (input) input.click();
};

// 组件卸载时清理
onUnmounted(() => {
  stopRealtimeDetection();
  if (videoUrl.value) {
    URL.revokeObjectURL(videoUrl.value);
  }
});

const resetBatchState = () => {
  batchMode.value = false;
  batchTotal.value = 0;
  batchDone.value = 0;
  batchErrors.value = [];
  batchResults.value = [];
  batchCurrentIndex.value = 0;
};

// 监听选项卡切换，离开视频时停止检测，并清理批量进度
watch(activeTab, (newVal) => {
  if (newVal !== "video" && isRealtimeDetecting.value) {
    stopRealtimeDetection();
  }
  videoMode.value = newVal === "video";

  if (newVal === "video" || newVal === "single") {
    resetBatchState();
  }
});
</script>

<style scoped>
.detection-page {
  width: 100%;
  position: relative;
}

/* 页面头部 */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
}
.breadcrumb {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}
.breadcrumb-item {
  font-size: 13px;
  color: var(--text-muted);
}
.breadcrumb-item.active {
  color: var(--text-secondary);
  font-weight: 500;
}
.breadcrumb-separator {
  font-size: 12px;
  color: var(--text-muted);
}
.title-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  background: var(--accent-gradient);
  border-radius: 10px;
  margin-right: 10px;
  color: white;
  font-size: 18px;
  vertical-align: middle;
  box-shadow: var(--accent-glow);
}
.page-title {
  font-size: 22px;
  font-weight: 700;
  color: var(--text-heading);
  margin-bottom: 6px;
}
.page-subtitle {
  font-size: 13px;
  color: var(--text-muted);
}

.model-selector {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
}
.selector-icon {
  color: var(--accent-cyan);
  font-size: 16px;
}

/* 功能选项卡 */
.function-tabs {
  display: flex;
  gap: 12px;
  margin-bottom: 24px;
}
.function-tab {
  flex: 1;
  display: flex;
  align-items: center;
  padding: 18px 20px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
}
.function-tab:hover {
  border-color: var(--border-color);
}
.function-tab.active {
  border-color: var(--accent-cyan);
  box-shadow: var(--shadow-glow-cyan), var(--shadow-md);
}
.file-input {
  position: absolute;
  inset: 0;
  opacity: 0;
  cursor: pointer;
  z-index: 10;
}
.tab-icon-wrap {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 14px;
  flex-shrink: 0;
  background: rgba(6, 182, 212, 0.1);
  color: var(--accent-cyan);
  transition: all 0.3s;
}
.function-tab.active .tab-icon-wrap {
  background: var(--accent-gradient);
  color: white;
  box-shadow: 0 4px 16px rgba(6, 182, 212, 0.3);
}
.tab-content {
  display: flex;
  flex-direction: column;
}
.tab-text {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-heading);
  line-height: 1.4;
}
.tab-desc {
  font-size: 12px;
  color: var(--text-muted);
  line-height: 1.4;
  margin-top: 2px;
}
.tab-glow {
  position: absolute;
  top: -50%;
  right: -50%;
  width: 200px;
  height: 200px;
  background: radial-gradient(circle, rgba(6, 182, 212, 0.1), transparent 70%);
  pointer-events: none;
}

/* 主内容区域 */
.main-content {
  display: flex;
  gap: 20px;
  align-items: flex-start;
  min-width: 0;
  max-height: calc(100vh - 240px);
}

.left-panel {
  flex: 1;
  min-width: 0;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  max-height: 100%;
  overflow-y: auto;
}

.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}
.panel-title-wrap {
  display: flex;
  align-items: center;
  gap: 8px;
}
.panel-icon {
  font-size: 16px;
  color: var(--accent-cyan);
}
.panel-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-heading);
}
.wait-badge {
  background: rgba(100, 116, 139, 0.1) !important;
  border-color: rgba(100, 116, 139, 0.2) !important;
  color: var(--text-muted) !important;
}

.toolbar {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
}
.tool-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 7px 14px;
  background: rgba(15, 23, 42, 0.4);
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius-sm);
  color: var(--text-secondary);
  font-size: 13px;
  cursor: pointer;
  transition: all 0.3s;
}
.tool-btn:hover {
  border-color: var(--border-glow);
  color: var(--accent-cyan);
}
.tool-btn.active {
  background: rgba(6, 182, 212, 0.1);
  border-color: var(--accent-cyan);
  color: var(--accent-cyan);
  box-shadow: 0 0 12px rgba(6, 182, 212, 0.15);
}

.image-compare {
  display: flex;
  gap: 16px;
  flex: 0 0 auto;
  align-items: stretch;
}
.image-compare.single {
  max-height: 420px;
}
.image-compare.grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  flex: 0 0 auto;
  max-height: 420px;
}
.image-card {
  flex: 1;
  position: relative;
  display: flex;
  flex-direction: column;
  border-radius: var(--border-radius-md);
  overflow: hidden;
  background: rgba(15, 23, 42, 0.4);
  border: 1px solid var(--border-color);
  max-height: 420px;
}
.image-card.wide {
  flex: none;
  width: 100%;
}
.compare-image {
  width: 100%;
  flex: 1;
  min-height: 0;
  object-fit: contain;
}
.image-label {
  padding: 8px 10px;
  text-align: center;
  color: var(--text-secondary);
  font-size: 12px;
  font-weight: 500;
  background: rgba(15, 23, 42, 0.6);
  border-top: 1px solid var(--border-color);
}
.detection-mark {
  position: absolute;
  top: 12px;
  right: 12px;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: var(--success);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 16px;
  box-shadow: 0 4px 16px rgba(16, 185, 129, 0.4);
}

/* 右侧面板 */
.right-panel {
  flex: 0 0 200px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  min-height: 0;
  max-height: 100%;
  overflow-y: auto;
}

.info-card, .result-card {
  padding: 16px;
}

.card-title-small {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 14px;
  font-size: 13px;
  font-weight: 600;
  color: var(--text-heading);
}
.card-title-small .el-icon {
  font-size: 15px;
  color: var(--accent-cyan);
}

.info-header {
  cursor: pointer;
  justify-content: space-between;
}
.info-header span {
  flex: 1;
}
.toggle-indicator {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  transition: background 0.2s ease;
}
.info-header:hover .toggle-indicator {
  background: rgba(255, 255, 255, 0.08);
}
.info-collapsed-note {
  padding: 12px 0 4px;
  color: var(--text-muted);
  font-size: 12px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  border-bottom: 1px solid rgba(99, 102, 241, 0.1);
}
.info-item:last-child {
  border-bottom: none;
}
.info-label {
  font-size: 12px;
  color: var(--text-muted);
}
.info-value {
  font-size: 12px;
  font-weight: 500;
  color: var(--text-secondary);
}
.info-value.highlight {
  color: var(--accent-cyan);
  font-weight: 600;
}

.empty-state-mini {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 28px 0;
}
.empty-orb {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: rgba(16, 185, 129, 0.1);
  border: 1px solid rgba(16, 185, 129, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--success);
  font-size: 20px;
  margin-bottom: 10px;
}
.empty-text {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-secondary);
  margin-bottom: 2px;
}
.empty-desc {
  font-size: 12px;
  color: var(--text-muted);
}

/* 像素统计 */
.stats-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.stat-row {
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.stat-bar-wrapper {
  height: 6px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 3px;
  overflow: hidden;
}
.stat-bar {
  height: 100%;
  border-radius: 3px;
  transition: width 0.8s cubic-bezier(0.4, 0, 0.2, 1);
}
.stat-info {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
}
.stat-name {
  color: var(--text-secondary);
}
.stat-ratio {
  font-weight: 600;
  color: var(--accent-cyan);
}

/* 图例 */
.legend-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.legend-item {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 4px 10px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid var(--border-color);
  border-radius: 6px;
  font-size: 12px;
}
.legend-color {
  width: 12px;
  height: 12px;
  border-radius: 3px;
}
.legend-name {
  color: var(--text-secondary);
}

/* AI诊断 */
.diagnosis-content {
  display: flex;
  gap: 12px;
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.7;
}
.diagnosis-avatar {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  background: var(--accent-gradient);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 16px;
  flex-shrink: 0;
  box-shadow: var(--accent-glow);
}
.diagnosis-placeholder {
  color: var(--text-muted);
}
.highlight-text {
  color: var(--accent-cyan);
  font-weight: 600;
}

/* 操作按钮 */
.action-buttons {
  display: flex;
  gap: 12px;
}
.btn-secondary {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 11px;
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
  flex: 2;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 11px;
  font-size: 13px;
  font-weight: 600;
}

/* 批量进度条 */
.batch-progress-bar {
  padding: 16px 20px;
  margin-bottom: 16px;
}
.batch-progress-header {
  display: flex;
  justify-content: space-between;
  font-size: 13px;
  color: var(--text-muted);
  margin-bottom: 8px;
}
.batch-progress-track {
  height: 6px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 3px;
  overflow: hidden;
}
.batch-progress-fill {
  height: 100%;
  background: var(--accent-gradient);
  border-radius: 3px;
  transition: width 0.5s ease;
}
.batch-errors {
  margin-top: 8px;
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}
.batch-error-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #ef4444;
}

/* 批量缩略图条 */
.batch-thumbnail-strip {
  display: flex;
  gap: 8px;
  margin-top: 16px;
  padding: 10px;
  background: rgba(15, 23, 42, 0.3);
  border-radius: var(--border-radius-md);
  border: 1px solid var(--border-color);
  overflow-x: auto;
}
.batch-thumb {
  flex-shrink: 0;
  width: 80px;
  cursor: pointer;
  border: 2px solid var(--border-color);
  border-radius: 8px;
  overflow: hidden;
  transition: all 0.2s;
  background: rgba(15, 23, 42, 0.4);
}
.batch-thumb:hover {
  border-color: var(--border-glow);
}
.batch-thumb.active {
  border-color: var(--accent-cyan);
  box-shadow: 0 0 12px rgba(6, 182, 212, 0.3);
}
.batch-thumb img {
  width: 80px;
  height: 56px;
  object-fit: cover;
  display: block;
}
.batch-thumb .thumb-label {
  display: block;
  font-size: 10px;
  color: var(--text-muted);
  text-align: center;
  padding: 2px 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.batch-thumb.active .thumb-label {
  color: var(--accent-cyan);
}

/* AI建议提示 */
.advice-tip {
  margin-top: 8px;
  padding: 8px 12px;
  background: rgba(16, 185, 129, 0.08);
  border-left: 3px solid var(--success);
  border-radius: 0 6px 6px 0;
  font-size: 12px;
  color: var(--text-secondary);
  line-height: 1.6;
}

/* ─── 视频检测样式 ─── */
.video-panel {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.video-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 280px;
  border: 2px dashed var(--border-color);
  border-radius: var(--border-radius-md);
  cursor: pointer;
  transition: all 0.3s;
}
.video-placeholder:hover {
  border-color: var(--accent-cyan);
  background: rgba(6, 182, 212, 0.05);
}
.video-placeholder .placeholder-icon {
  color: var(--text-muted);
  margin-bottom: 12px;
}
.video-placeholder .placeholder-text {
  font-size: 14px;
  color: var(--text-secondary);
  margin-bottom: 4px;
}
.video-placeholder .placeholder-desc {
  font-size: 12px;
  color: var(--text-muted);
}

/* 左右对比容器 */
.video-compare-wrap {
  display: flex;
  gap: 16px;
  flex: 1;
  min-height: 0;
  align-items: stretch;
}
.video-compare-card {
  flex: 1;
  position: relative;
  border-radius: var(--border-radius-md);
  overflow: hidden;
  background: rgba(15, 23, 42, 0.4);
  border: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
  max-height: 420px;
}
.video-compare-card .video-player-wrap {
  flex: 1;
  min-height: 0;
  background: #000;
  display: flex;
  align-items: center;
  justify-content: center;
}
.video-compare-card .video-player {
  width: 100%;
  height: 100%;
  max-height: 420px;
  display: block;
  object-fit: contain;
}
.video-result-img {
  width: 100%;
  height: 100%;
  object-fit: contain;
  display: block;
}
.param-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.param-label {
  font-size: 13px;
  color: var(--text-secondary);
}
.param-tip {
  font-size: 11px;
  color: var(--text-muted);
}

/* 折叠卡片 */
.collapsible-card {
  overflow: hidden;
}
.collapsible-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  cursor: pointer;
  user-select: none;
  margin-bottom: 0;
  padding: 2px 0;
}
.collapsible-header:hover {
  color: var(--accent-cyan);
}
.collapsible-header .header-left {
  display: flex;
  align-items: center;
  gap: 8px;
}
.collapse-arrow {
  font-size: 14px;
  color: var(--text-muted);
  transition: transform 0.3s ease;
}
.collapse-arrow.rotated {
  transform: rotate(90deg);
}
.collapsible-body {
  padding-top: 14px;
  animation: collapseIn 0.25s ease;
}
@keyframes collapseIn {
  from {
    opacity: 0;
    transform: translateY(-6px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
