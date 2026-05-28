<template>
  <div class="targets-page">
    <!-- 页面头部 -->
    <div class="page-header animate-fade-in-up">
      <h1 class="page-title">7 类地物说明</h1>
      <p class="page-subtitle">
        模型在 LoveDA 数据集上训练，共 7 类土地类型。以下为验证集上的 IoU 表现。
      </p>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-row animate-fade-in-up" style="animation-delay: 0.08s">
      <div class="stat-card glass-card">
        <div class="stat-bg-glow cyan"></div>
        <div class="stat-icon-wrap cyan">
          <el-icon><Aim /></el-icon>
        </div>
        <div class="stat-data">
          <div class="stat-num">7</div>
          <div class="stat-label">训练类别</div>
        </div>
      </div>
      <div class="stat-card glass-card">
        <div class="stat-bg-glow purple"></div>
        <div class="stat-icon-wrap purple">
          <el-icon><TrendCharts /></el-icon>
        </div>
        <div class="stat-data">
          <div class="stat-num">68.7%</div>
          <div class="stat-label">平均 Val IoU</div>
        </div>
      </div>
      <div class="stat-card glass-card">
        <div class="stat-bg-glow green"></div>
        <div class="stat-icon-wrap green">
          <el-icon><Trophy /></el-icon>
        </div>
        <div class="stat-data">
          <div class="stat-num">79.5%</div>
          <div class="stat-label">最高 Val IoU</div>
        </div>
      </div>
      <div class="stat-card glass-card">
        <div class="stat-bg-glow pink"></div>
        <div class="stat-icon-wrap pink">
          <el-icon><Cpu /></el-icon>
        </div>
        <div class="stat-data">
          <div class="stat-num">land-seg-v1</div>
          <div class="stat-label">模型版本</div>
        </div>
      </div>
    </div>

    <!-- IoU 总览条形图 -->
    <div class="iou-overview glass-card animate-fade-in-up" style="animation-delay: 0.12s">
      <div class="overview-header">
        <el-icon><Histogram /></el-icon>
        <span>各类别 Val IoU 总览</span>
      </div>
      <div class="overview-list">
        <div
          v-for="item in sortedLandClasses"
          :key="item.id"
          class="overview-row"
          @click="showDetail(item)"
        >
          <div class="overview-color" :style="{ background: item.color }"></div>
          <div class="overview-name">
            <span class="name-zh">{{ item.name }}</span>
            <span class="name-en">{{ item.english }}</span>
          </div>
          <div class="overview-bar-wrap">
            <div
              class="overview-bar"
              :style="{ width: item.iou + '%', background: item.color }"
            ></div>
          </div>
          <div class="overview-value" :style="{ color: item.color }">{{ item.iou }}%</div>
        </div>
      </div>
    </div>

    <!-- 类别详情卡片 -->
    <div class="detail-grid animate-fade-in-up" style="animation-delay: 0.16s">
      <div
        v-for="(item, index) in sortedLandClasses"
        :key="item.id"
        class="detail-card glass-card"
        :style="{ animationDelay: `${0.2 + index * 0.05}s` }"
        @click="showDetail(item)"
      >
        <div class="card-accent" :style="{ background: item.color }"></div>
        <div class="card-top">
          <div class="card-color-block" :style="{ background: item.color, boxShadow: `0 4px 16px ${item.color}44` }">
            <el-icon :size="22"><component :is="item.icon" /></el-icon>
          </div>
          <div class="card-title-wrap">
            <div class="card-title">{{ item.name }}</div>
            <div class="card-subtitle">{{ item.english }}</div>
          </div>
        </div>
        <div class="card-desc">{{ item.description }}</div>
        <div class="card-iou">
          <div class="iou-label">Val IoU</div>
          <div class="iou-bar-wrap">
            <div class="iou-bar-bg">
              <div class="iou-bar-fill" :style="{ width: item.iou + '%', background: item.color }"></div>
            </div>
            <div class="iou-num" :style="{ color: item.color }">{{ item.iou }}%</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 详情弹窗 -->
    <el-dialog
      v-if="selectedItem"
      :title="selectedItem.name"
      v-model="showDialog"
      width="400px"
      class="detail-dialog"
    >
      <div class="detail-content">
        <div
          class="detail-color-icon"
          :style="{ background: selectedItem.color, boxShadow: `0 8px 32px ${selectedItem.color}44` }"
        >
          <el-icon :size="32"><component :is="selectedItem.icon" /></el-icon>
        </div>
        <div class="detail-name">{{ selectedItem.name }}</div>
        <div class="detail-en">{{ selectedItem.english }}</div>
        <div class="detail-tag" :style="{ color: selectedItem.color, background: selectedItem.color + '18', border: `1px solid ${selectedItem.color}33` }">
          Val IoU: {{ selectedItem.iou }}%
        </div>
        <div class="detail-info-list">
          <div class="detail-info-item">
            <span class="info-label">类型说明</span>
            <span class="info-value">{{ selectedItem.description }}</span>
          </div>
          <div class="detail-info-item">
            <span class="info-label">分割颜色</span>
            <span class="info-value" style="display:flex;align-items:center;gap:8px">
              <span class="color-dot" :style="{ background: selectedItem.color }"></span>
              {{ selectedItem.color }}
            </span>
          </div>
          <div class="detail-info-item">
            <span class="info-label">类别 ID</span>
            <span class="info-value">{{ selectedItem.id }}</span>
          </div>
          <div class="detail-info-item">
            <span class="info-label">模型支持</span>
            <span class="info-value">land-seg-v1 (DeepLabV3+ / ResNet50)</span>
          </div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed } from "vue";
import {
  Aim, TrendCharts, Trophy, Cpu, Histogram,
  Hide, OfficeBuilding, TopRight, Pouring, MapLocation, Sunny, Crop,
} from "@element-plus/icons-vue";

const showDialog = ref(false);
const selectedItem = ref(null);

// 7 类地物真实数据（与后端 LAND_CLASSES 和训练结果一致）
const landClasses = ref([
  {
    id: 0, name: "背景", english: "Background",
    color: "#000000", iou: 77.18,
    description: "图像边缘或无意义区域",
    icon: Hide,
  },
  {
    id: 1, name: "建筑", english: "Building",
    color: "#FF0000", iou: 61.77,
    description: "房屋、厂房、大棚等人工建筑",
    icon: OfficeBuilding,
  },
  {
    id: 2, name: "道路", english: "Road",
    color: "#FFFF00", iou: 62.94,
    description: "公路、乡村道路等交通道路",
    icon: TopRight,
  },
  {
    id: 3, name: "水域", english: "Water",
    color: "#0000FF", iou: 65.98,
    description: "河流、湖泊、池塘等水体",
    icon: Pouring,
  },
  {
    id: 4, name: "裸地", english: "Barren",
    color: "#8B4513", iou: 79.51,
    description: "未耕种土地、荒地",
    icon: MapLocation,
  },
  {
    id: 5, name: "林地", english: "Forest",
    color: "#008000", iou: 58.91,
    description: "森林、树木覆盖区",
    icon: Sunny,
  },
  {
    id: 6, name: "耕地", english: "Agriculture",
    color: "#00FF00", iou: 74.40,
    description: "农田、种植区",
    icon: Crop,
  },
]);

// 按 IoU 从高到低排序
const sortedLandClasses = computed(() => {
  return [...landClasses.value].sort((a, b) => b.iou - a.iou);
});

const showDetail = (item) => {
  selectedItem.value = item;
  showDialog.value = true;
};
</script>

<style scoped>
.targets-page {
  width: 100%;
}

.page-header {
  margin-bottom: 24px;
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

/* 统计卡片 */
.stats-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}
.stat-card {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 18px;
  position: relative;
  overflow: hidden;
}
.stat-bg-glow {
  position: absolute;
  top: -20px;
  right: -20px;
  width: 80px;
  height: 80px;
  border-radius: 50%;
  filter: blur(30px);
  opacity: 0.2;
  pointer-events: none;
}
.stat-bg-glow.cyan { background: var(--accent-cyan); }
.stat-bg-glow.purple { background: var(--accent-purple); }
.stat-bg-glow.green { background: var(--success); }
.stat-bg-glow.pink { background: #ec4899; }

.stat-icon-wrap {
  width: 46px;
  height: 46px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 20px;
  flex-shrink: 0;
}
.stat-icon-wrap.cyan { background: linear-gradient(135deg, #06b6d4, #0891b2); box-shadow: 0 4px 16px rgba(6, 182, 212, 0.3); }
.stat-icon-wrap.purple { background: linear-gradient(135deg, #8b5cf6, #7c3aed); box-shadow: 0 4px 16px rgba(139, 92, 246, 0.3); }
.stat-icon-wrap.green { background: linear-gradient(135deg, #10b981, #059669); box-shadow: 0 4px 16px rgba(16, 185, 129, 0.3); }
.stat-icon-wrap.pink { background: linear-gradient(135deg, #ec4899, #db2777); box-shadow: 0 4px 16px rgba(236, 72, 153, 0.3); }

.stat-data { line-height: 1.3; }
.stat-num { font-size: 20px; font-weight: 700; color: var(--text-heading); }
.stat-label { font-size: 12px; color: var(--text-muted); }

/* IoU 总览 */
.iou-overview {
  padding: 20px;
  margin-bottom: 24px;
}
.overview-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 600;
  color: var(--text-heading);
  margin-bottom: 18px;
}
.overview-header .el-icon { color: var(--accent-cyan); }

.overview-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.overview-row {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 10px;
  background: rgba(15, 23, 42, 0.4);
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius-sm);
  cursor: pointer;
  transition: all 0.25s;
}
.overview-row:hover {
  border-color: var(--border-glow);
  transform: translateX(4px);
}
.overview-color {
  width: 14px;
  height: 14px;
  border-radius: 4px;
  flex-shrink: 0;
  border: 1px solid rgba(255,255,255,0.1);
}
.overview-name {
  width: 100px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  gap: 1px;
}
.name-zh {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-heading);
}
.name-en {
  font-size: 11px;
  color: var(--text-muted);
}
.overview-bar-wrap {
  flex: 1;
  height: 8px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 4px;
  overflow: hidden;
}
.overview-bar {
  height: 100%;
  border-radius: 4px;
  transition: width 0.8s cubic-bezier(0.4, 0, 0.2, 1);
}
.overview-value {
  width: 52px;
  text-align: right;
  font-size: 13px;
  font-weight: 700;
  flex-shrink: 0;
}

/* 详情卡片网格 */
.detail-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}
.detail-card {
  padding: 18px;
  position: relative;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s;
}
.detail-card:hover {
  transform: translateY(-2px);
  border-color: var(--border-glow);
}
.card-accent {
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 3px;
  opacity: 0.8;
}
.card-top {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}
.card-color-block {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 18px;
  flex-shrink: 0;
}
.card-title-wrap { line-height: 1.3; }
.card-title { font-size: 15px; font-weight: 600; color: var(--text-heading); }
.card-subtitle { font-size: 11px; color: var(--text-muted); margin-top: 2px; }
.card-desc {
  font-size: 12px;
  color: var(--text-secondary);
  line-height: 1.5;
  margin-bottom: 14px;
  min-height: 36px;
}
.card-iou {
  margin-top: auto;
}
.iou-label {
  font-size: 11px;
  color: var(--text-muted);
  margin-bottom: 6px;
}
.iou-bar-wrap {
  display: flex;
  align-items: center;
  gap: 10px;
}
.iou-bar-bg {
  flex: 1;
  height: 6px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 3px;
  overflow: hidden;
}
.iou-bar-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 0.8s cubic-bezier(0.4, 0, 0.2, 1);
}
.iou-num {
  font-size: 13px;
  font-weight: 700;
  width: 48px;
  text-align: right;
  flex-shrink: 0;
}

/* 详情弹窗 */
.detail-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 10px 0;
}
.detail-color-icon {
  width: 64px;
  height: 64px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  margin-bottom: 14px;
}
.detail-name { font-size: 20px; font-weight: 700; color: var(--text-heading); margin-bottom: 4px; }
.detail-en { font-size: 13px; color: var(--text-muted); margin-bottom: 10px; }
.detail-tag {
  padding: 4px 14px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 600;
  margin-bottom: 18px;
}
.detail-info-list { width: 100%; }
.detail-info-item {
  display: flex;
  justify-content: space-between;
  padding: 12px 0;
  border-bottom: 1px solid rgba(99, 102, 241, 0.1);
}
.detail-info-item:last-child { border-bottom: none; }
.info-label { font-size: 13px; color: var(--text-muted); }
.info-value { font-size: 13px; color: var(--text-secondary); font-weight: 500; max-width: 55%; text-align: right; }
.color-dot {
  width: 14px;
  height: 14px;
  border-radius: 4px;
  display: inline-block;
  border: 1px solid rgba(255,255,255,0.1);
}

@media (max-width: 1024px) {
  .stats-row { grid-template-columns: repeat(2, 1fr); }
  .detail-grid { grid-template-columns: repeat(2, 1fr); }
  .palette-grid { grid-template-columns: repeat(2, 1fr); }
}
@media (max-width: 768px) {
  .stats-row { grid-template-columns: 1fr; }
  .detail-grid { grid-template-columns: 1fr; }
  .palette-grid { grid-template-columns: 1fr; }
  .overview-name { width: 70px; }
}
</style>
