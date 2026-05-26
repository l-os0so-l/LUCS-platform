<template>
  <div class="targets-page">
    <!-- 页面头部 -->
    <div class="page-header animate-fade-in-up">
      <h1 class="page-title">土地类型库</h1>
      <p class="page-subtitle">平台支持分类的所有土地类型，覆盖耕地、林地、水域、建筑等大类</p>
    </div>

    <!-- 搜索框 -->
    <div class="search-container animate-fade-in-up" style="animation-delay: 0.08s">
      <div class="search-wrap">
        <el-icon class="search-icon"><Search /></el-icon>
        <el-input
          v-model="searchQuery"
          placeholder="搜索土地类型..."
          size="default"
          class="search-input"
        />
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-row animate-fade-in-up" style="animation-delay: 0.12s">
      <div class="stat-card glass-card">
        <div class="stat-bg-glow cyan"></div>
        <div class="stat-icon-wrap cyan">
          <el-icon><Aim /></el-icon>
        </div>
        <div class="stat-data">
          <div class="stat-num">{{ totalTargets }}</div>
          <div class="stat-label">类型总数</div>
        </div>
      </div>
      <div class="stat-card glass-card">
        <div class="stat-bg-glow purple"></div>
        <div class="stat-icon-wrap purple">
          <el-icon><Grid /></el-icon>
        </div>
        <div class="stat-data">
          <div class="stat-num">{{ categories.length }}</div>
          <div class="stat-label">类别数量</div>
        </div>
      </div>
      <div class="stat-card glass-card">
        <div class="stat-bg-glow green"></div>
        <div class="stat-icon-wrap green">
          <el-icon><TrendCharts /></el-icon>
        </div>
        <div class="stat-data">
          <div class="stat-num">98.5%</div>
          <div class="stat-label">平均精度</div>
        </div>
      </div>
    </div>

    <!-- 土地类型列表 -->
    <div class="target-categories">
      <div
        v-for="(category, index) in filteredCategories"
        :key="category.id"
        class="category-card glass-card animate-fade-in-up"
        :style="{ animationDelay: `${0.15 + index * 0.06}s` }"
      >
        <div class="category-accent" :style="{ background: category.color }"></div>
        <div class="category-header">
          <div class="category-icon" :style="{ background: category.color, boxShadow: `0 4px 16px ${category.color}44` }">
            <component :is="category.icon" />
          </div>
          <div class="category-info">
            <div class="category-name">{{ category.name }}</div>
            <div class="category-count">{{ category.targets.length }} 个类型</div>
          </div>
        </div>
        <div class="target-list">
          <div
            v-for="target in category.targets"
            :key="target.id"
            class="target-item"
            @click="showTargetDetail(target)"
          >
            <span class="target-dot" :style="{ background: category.color, boxShadow: `0 0 6px ${category.color}66` }"></span>
            <span class="target-name">{{ target.name }}</span>
            <span class="target-accuracy">{{ target.accuracy }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 空状态 -->
    <div v-if="filteredCategories.length === 0" class="empty-state animate-fade-in-up">
      <div class="empty-orb">
        <el-icon :size="48"><Search /></el-icon>
      </div>
      <p class="empty-text">未找到匹配的土地类型</p>
      <p class="empty-desc">尝试使用其他关键词搜索</p>
    </div>

    <!-- 类型详情弹窗 -->
    <el-dialog
      v-if="selectedTarget"
      :title="selectedTarget.name"
      v-model="showDialog"
      width="420px"
      class="detail-dialog"
    >
      <div class="target-detail">
        <div class="detail-icon" :style="{ background: getCategoryColor(selectedTarget.categoryId), boxShadow: `0 8px 32px ${getCategoryColor(selectedTarget.categoryId)}44` }">
          <el-icon :size="40"><component :is="getCategoryIcon(selectedTarget.categoryId)" /></el-icon>
        </div>
        <div class="detail-name">{{ selectedTarget.name }}</div>
        <div class="detail-tag" :style="{ color: getCategoryColor(selectedTarget.categoryId), background: getCategoryColor(selectedTarget.categoryId) + '18', border: `1px solid ${getCategoryColor(selectedTarget.categoryId)}33` }">
          {{ getCategoryName(selectedTarget.categoryId) }}
        </div>
        <div class="detail-info">
          <div class="detail-item">
            <span class="detail-label">类型描述</span>
            <span class="detail-value">{{ selectedTarget.description }}</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">分类精度</span>
            <span class="detail-value highlight">{{ selectedTarget.accuracy }}</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">模型支持</span>
            <span class="detail-value">land-seg-v1</span>
          </div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed } from "vue";
import {
  Search, Aim, Grid, CircleCheck, Help,
  OfficeBuilding, Sunny, Setting, TrendCharts,
  Bicycle,
} from "@element-plus/icons-vue";

const searchQuery = ref("");
const showDialog = ref(false);
const selectedTarget = ref(null);

const categories = ref([
  {
    id: 1, name: "耕地类型", icon: Bicycle, color: "#06b6d4",
    targets: [
      { id: 1, name: "耕地", categoryId: 1, description: "连片耕作农田", accuracy: "98.5%" },
      { id: 2, name: "水田", categoryId: 1, description: "水稻种植区域", accuracy: "97.2%" },
      { id: 3, name: "旱地", categoryId: 1, description: "旱作农业区域", accuracy: "96.8%" },
      { id: 4, name: "农田", categoryId: 1, description: "各类耕种农田", accuracy: "95.6%" },
      { id: 5, name: "园地", categoryId: 1, description: "果园、茶园等园地", accuracy: "94.3%" },
    ],
  },
  {
    id: 2, name: "建筑类型", icon: OfficeBuilding, color: "#8b5cf6",
    targets: [
      { id: 6, name: "建筑", categoryId: 2, description: "居民建筑、工业建筑", accuracy: "99.1%" },
      { id: 7, name: "居民地", categoryId: 2, description: "城乡居民区", accuracy: "97.8%" },
      { id: 8, name: "道路", categoryId: 2, description: "公路、城市道路", accuracy: "96.4%" },
      { id: 9, name: "工业区", categoryId: 2, description: "工业园区、厂房", accuracy: "95.9%" },
      { id: 10, name: "城市", categoryId: 2, description: "城市建成区", accuracy: "98.7%" },
    ],
  },
  {
    id: 3, name: "林地水域", icon: Sunny, color: "#10b981",
    targets: [
      { id: 11, name: "林地", categoryId: 3, description: "乔木林地、灌木林地", accuracy: "99.5%" },
      { id: 12, name: "森林", categoryId: 3, description: "成片森林覆盖区", accuracy: "98.9%" },
      { id: 13, name: "草地", categoryId: 3, description: "草地、牧草地", accuracy: "97.6%" },
      { id: 14, name: "水域", categoryId: 3, description: "河流、湖泊等水体", accuracy: "96.2%" },
      { id: 15, name: "水库", categoryId: 3, description: "人工水库、水塘", accuracy: "95.4%" },
    ],
  },
  {
    id: 4, name: "其他类型", icon: Setting, color: "#ec4899",
    targets: [
      { id: 16, name: "裸地", categoryId: 4, description: "未利用裸土地", accuracy: "98.3%" },
      { id: 17, name: "沼泽", categoryId: 4, description: "沼泽湿地", accuracy: "97.1%" },
      { id: 18, name: "湿地", categoryId: 4, description: "河流、湖泊湿地", accuracy: "96.7%" },
      { id: 19, name: "荒漠", categoryId: 4, description: "荒漠、沙地", accuracy: "95.8%" },
      { id: 20, name: "盐碱地", categoryId: 4, description: "盐碱地、滩涂", accuracy: "94.9%" },
    ],
  },
]);

const filteredCategories = computed(() => {
  if (!searchQuery.value) return categories.value;
  const query = searchQuery.value.toLowerCase();
  return categories.value.map((category) => ({
    ...category,
    targets: category.targets.filter((target) =>
      target.name.toLowerCase().includes(query)
    ),
  })).filter((category) =>
    category.name.toLowerCase().includes(query) || category.targets.length > 0
  );
});

const totalTargets = computed(() =>
  categories.value.reduce((sum, category) => sum + category.targets.length, 0)
);

const getCategoryColor = (categoryId) => {
  const category = categories.value.find((c) => c.id === categoryId);
  return category ? category.color : "#6b7280";
};
const getCategoryIcon = (categoryId) => {
  const category = categories.value.find((c) => c.id === categoryId);
  return category ? category.icon : Setting;
};
const getCategoryName = (categoryId) => {
  const category = categories.value.find((c) => c.id === categoryId);
  return category ? category.name : "未知";
};
const showTargetDetail = (target) => {
  selectedTarget.value = target;
  showDialog.value = true;
};
</script>

<style scoped>
.targets-page {
  width: 100%;
}

.search-container {
  margin-bottom: 20px;
}
.search-wrap {
  max-width: 320px;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 0 12px;
  background: rgba(15, 23, 42, 0.6);
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius-md);
  transition: all 0.3s;
}
.search-wrap:hover,
.search-wrap:focus-within {
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

.stats-row {
  display: flex;
  gap: 16px;
  margin-bottom: 24px;
}
.stat-card {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
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

.stat-icon-wrap {
  width: 50px;
  height: 50px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 22px;
  flex-shrink: 0;
}
.stat-icon-wrap.cyan { background: linear-gradient(135deg, #06b6d4, #0891b2); box-shadow: 0 4px 16px rgba(6, 182, 212, 0.3); }
.stat-icon-wrap.purple { background: linear-gradient(135deg, #8b5cf6, #7c3aed); box-shadow: 0 4px 16px rgba(139, 92, 246, 0.3); }
.stat-icon-wrap.green { background: linear-gradient(135deg, #10b981, #059669); box-shadow: 0 4px 16px rgba(16, 185, 129, 0.3); }

.stat-data {
  line-height: 1.3;
}
.stat-num {
  font-size: 24px;
  font-weight: 700;
  color: var(--text-heading);
}
.stat-label {
  font-size: 12px;
  color: var(--text-muted);
}

/* 类别卡片 */
.target-categories {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
}
.category-card {
  padding: 20px;
  position: relative;
  overflow: hidden;
}
.category-accent {
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 3px;
  opacity: 0.8;
}
.category-header {
  display: flex;
  align-items: center;
  margin-bottom: 18px;
}
.category-icon {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 22px;
  margin-right: 14px;
}
.category-info {
  line-height: 1.3;
}
.category-name {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-heading);
  margin-bottom: 3px;
}
.category-count {
  font-size: 12px;
  color: var(--text-muted);
}

.target-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.target-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  background: rgba(15, 23, 42, 0.4);
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius-sm);
  font-size: 13px;
  cursor: pointer;
  transition: all 0.3s;
}
.target-item:hover {
  border-color: var(--border-glow);
  background: rgba(6, 182, 212, 0.05);
  transform: translateX(4px);
}
.target-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  flex-shrink: 0;
}
.target-name {
  color: var(--text-secondary);
  flex: 1;
}
.target-item:hover .target-name {
  color: var(--text-primary);
}
.target-accuracy {
  font-size: 11px;
  font-weight: 600;
  color: var(--accent-cyan);
  padding: 2px 8px;
  background: rgba(6, 182, 212, 0.08);
  border-radius: 10px;
}

.empty-orb {
  width: 72px;
  height: 72px;
  border-radius: 50%;
  background: rgba(99, 102, 241, 0.08);
  border: 1px solid rgba(99, 102, 241, 0.15);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-muted);
  margin-bottom: 16px;
}

/* 详情弹窗 */
.target-detail {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 10px 0;
}
.detail-icon {
  width: 72px;
  height: 72px;
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  margin-bottom: 16px;
}
.detail-name {
  font-size: 20px;
  font-weight: 700;
  color: var(--text-heading);
  margin-bottom: 8px;
}
.detail-tag {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
  margin-bottom: 20px;
}
.detail-info {
  width: 100%;
}
.detail-item {
  display: flex;
  justify-content: space-between;
  padding: 12px 0;
  border-bottom: 1px solid rgba(99, 102, 241, 0.1);
}
.detail-item:last-child {
  border-bottom: none;
}
.detail-label {
  font-size: 13px;
  color: var(--text-muted);
}
.detail-value {
  font-size: 13px;
  color: var(--text-secondary);
  font-weight: 500;
  max-width: 55%;
  text-align: right;
}
.detail-value.highlight {
  color: var(--accent-cyan);
  font-weight: 700;
}

@media (max-width: 768px) {
  .target-categories {
    grid-template-columns: 1fr;
  }
  .stats-row {
    flex-direction: column;
  }
}
</style>
