<template>
  <div class="container">
    <h1>🌍 土地利用分类系统</h1>

    <!-- 上传组件 -->
    <el-upload
      class="upload-area"
      action="#"
      :auto-upload="false"
      :on-change="handleFileChange"
      :before-upload="beforeUpload"
    >
      <el-button type="primary">选择图片上传</el-button>
      <template #tip>
        <div class="el-upload__tip">支持 jpg/png 格式，大小不超过 5MB</div>
      </template>
    </el-upload>

    <!-- 分类按钮 -->
    <el-button
      type="success"
      style="margin-top: 20px"
      @click="handleInference"
      :disabled="!selectedFile || loading"
    >
      {{ loading ? "分类中..." : "开始分类" }}
    </el-button>

    <!-- 结果展示 -->
    <div v-if="resultImageUrl" class="result-container">
      <h3>分类结果：</h3>
      <img :src="resultImageUrl" alt="分类结果" class="result-img" />
      <div class="detections-list">
        <el-tag v-for="(item, index) in detections" :key="index" type="success">
          {{ item.class }}: {{ (item.confidence * 100).toFixed(1) }}%
        </el-tag>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import axios from "axios";
import { ElMessage } from "element-plus";

const selectedFile = ref(null);
const loading = ref(false);
const resultImageUrl = ref("");
const detections = ref([]);

// 文件选择
const handleFileChange = (file) => {
  selectedFile.value = file.raw;
  resultImageUrl.value = "";
  detections.value = [];
};

// 上传前校验
const beforeUpload = (file) => {
  const isImage = ["image/jpeg", "image/png"].includes(file.type);
  const isLt5M = file.size / 1024 / 1024 < 5;
  if (!isImage) {
    ElMessage.error("请上传 jpg/png 格式图片");
    return false;
  }
  if (!isLt5M) {
    ElMessage.error("图片大小不能超过 5MB");
    return false;
  }
  return true;
};

// 调用推理接口
const handleInference = async () => {
  if (!selectedFile.value) return;

  loading.value = true;
  const formData = new FormData();
  formData.append("file", selectedFile.value);

  try {
    const res = await axios.post("http://localhost:8000/api/inference/single", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });

    if (res.data.code === 200) {
      ElMessage.success("推理成功！");
      resultImageUrl.value = res.data.data.image_url;
      detections.value = res.data.data.detections;
    } else {
      ElMessage.error(res.data.message || "推理失败");
    }
  } catch (err) {
    ElMessage.error(`请求失败: ${err.message}`);
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.container {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

.upload-area {
  margin-top: 20px;
}

.result-container {
  margin-top: 30px;
}

.result-img {
  max-width: 100%;
  border-radius: 8px;
  margin-top: 10px;
}

.detections-list {
  margin-top: 15px;
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  justify-content: center;
}
</style>
