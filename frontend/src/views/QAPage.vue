<template>
  <div class="qa-page">
    <!-- 页面头部 -->
    <div class="page-header animate-fade-in-up">
      <div class="header-icon-wrap">
        <el-icon><ChatDotRound /></el-icon>
      </div>
      <div class="header-text">
        <h1 class="page-title">AI 智能问答</h1>
        <p class="page-subtitle">关于土地利用分类的任何问题，都可以问我</p>
      </div>
    </div>

    <!-- 快捷问题标签 -->
    <div class="quick-tags animate-fade-in-up" style="animation-delay: 0.1s">
      <span class="quick-label">常见问题：</span>
      <button
        v-for="tag in quickQuestions"
        :key="tag"
        class="quick-tag"
        @click="askQuick(tag)"
      >
        {{ tag }}
      </button>
    </div>

    <!-- 聊天容器 -->
    <div class="chat-container glass-card animate-fade-in-up" style="animation-delay: 0.15s">
      <div class="chat-messages" ref="messagesRef">
        <div
          v-for="(msg, index) in messages"
          :key="index"
          class="message"
          :class="msg.role"
        >
          <div class="message-avatar" :class="msg.role">
            <el-icon v-if="msg.role === 'ai'"><ChatDotRound /></el-icon>
            <el-icon v-else><User /></el-icon>
          </div>
          <div class="message-bubble">
            <div class="message-content">{{ msg.content }}</div>
            <div class="message-time">{{ msg.time }}</div>
          </div>
        </div>

        <!-- AI 正在输入 -->
        <div v-if="isTyping" class="message ai">
          <div class="message-avatar ai">
            <el-icon><ChatDotRound /></el-icon>
          </div>
          <div class="message-bubble">
            <div class="typing-indicator">
              <span></span><span></span><span></span>
            </div>
          </div>
        </div>
      </div>

      <div class="chat-input-area">
        <div class="input-wrapper">
          <el-input
            v-model="question"
            placeholder="请输入你的问题..."
            :rows="2"
            type="textarea"
            resize="none"
            @keydown.enter.prevent="sendMessage"
          />
          <button
            class="send-btn"
            :class="{ active: question.trim() }"
            @click="sendMessage"
            :disabled="!question.trim() || sending"
          >
            <el-icon><Promotion /></el-icon>
          </button>
        </div>
        <div class="input-hint">按 Enter 发送，Shift + Enter 换行</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick } from "vue";
import { ChatDotRound, User, Promotion } from "@element-plus/icons-vue";

const question = ref("");
const sending = ref(false);
const isTyping = ref(false);
const messagesRef = ref(null);

const quickQuestions = [
  "什么是土地利用分类？",
  "支持哪些土地类型？",
  "分类精度有多少？",
  "如何提高分类准确率？",
];

const messages = ref([
  {
    role: "ai",
    content: "你好！我是土地利用分类AI助手。我可以帮你解答关于耕地、林地、水域、建筑等土地类型分类的相关问题，也可以为你提供分类结果的详细分析。有什么可以帮你的吗？",
    time: getCurrentTime(),
  },
]);

function getCurrentTime() {
  const now = new Date();
  return `${now.getHours().toString().padStart(2, "0")}:${now.getMinutes().toString().padStart(2, "0")}`;
}

function scrollToBottom() {
  nextTick(() => {
    if (messagesRef.value) {
      messagesRef.value.scrollTop = messagesRef.value.scrollHeight;
    }
  });
}

function askQuick(tag) {
  question.value = tag;
  sendMessage();
}

async function sendMessage() {
  const text = question.value.trim();
  if (!text || sending.value) return;

  messages.value.push({ role: "user", content: text, time: getCurrentTime() });
  question.value = "";
  sending.value = true;
  scrollToBottom();

  // 模拟 AI 思考
  isTyping.value = true;
  scrollToBottom();

  await new Promise((r) => setTimeout(r, 1500));

  isTyping.value = false;
  const replies = [
    "这是一个很好的问题！根据平台的算法模型，我们可以精准识别多达20种土地类型，包括耕地、林地、水域、建筑等。",
    "平台的分类精度平均达到98.5%以上，采用的是DeepLabV3+架构结合ResNet50骨干网络。",
    "建议您上传清晰度较高的遥感影像，分辨率越高，分类效果越好。同时选择合适的模型也很重要。",
    "遥感影像的土地利用分类是环境监测、城市规划等领域的重要技术手段。",
  ];
  messages.value.push({
    role: "ai",
    content: replies[Math.floor(Math.random() * replies.length)],
    time: getCurrentTime(),
  });
  sending.value = false;
  scrollToBottom();
}
</script>

<style scoped>
.qa-page {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  max-width: 900px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  align-items: center;
  gap: 14px;
  margin-bottom: 16px;
}
.header-icon-wrap {
  width: 48px;
  height: 48px;
  border-radius: 14px;
  background: var(--accent-gradient);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 22px;
  box-shadow: var(--accent-glow);
  flex-shrink: 0;
}

.quick-tags {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
  margin-bottom: 16px;
}
.quick-label {
  font-size: 12px;
  color: var(--text-muted);
}
.quick-tag {
  padding: 6px 14px;
  background: rgba(6, 182, 212, 0.08);
  border: 1px solid rgba(6, 182, 212, 0.2);
  border-radius: 20px;
  color: var(--accent-cyan);
  font-size: 12px;
  cursor: pointer;
  transition: all 0.3s;
}
.quick-tag:hover {
  background: rgba(6, 182, 212, 0.15);
  border-color: var(--accent-cyan);
  box-shadow: 0 0 12px rgba(6, 182, 212, 0.15);
}

.chat-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  padding: 0;
}

.chat-messages {
  flex: 1;
  padding: 24px;
  overflow-y: auto;
}

.message {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
  animation: fadeInUp 0.3s ease-out;
}
.message.user {
  flex-direction: row-reverse;
}

.message-avatar {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  flex-shrink: 0;
}
.message-avatar.ai {
  background: var(--accent-gradient);
  color: white;
  box-shadow: var(--accent-glow);
}
.message-avatar.user {
  background: rgba(99, 102, 241, 0.15);
  border: 1px solid rgba(99, 102, 241, 0.3);
  color: var(--accent-purple);
}

.message-bubble {
  max-width: 70%;
  padding: 12px 16px;
  border-radius: 14px;
  position: relative;
}
.message.ai .message-bubble {
  background: rgba(15, 23, 42, 0.6);
  border: 1px solid var(--border-color);
  border-top-left-radius: 4px;
}
.message.user .message-bubble {
  background: rgba(6, 182, 212, 0.1);
  border: 1px solid rgba(6, 182, 212, 0.2);
  border-top-right-radius: 4px;
}

.message-content {
  font-size: 14px;
  line-height: 1.7;
  color: var(--text-secondary);
}
.message-time {
  font-size: 11px;
  color: var(--text-muted);
  margin-top: 6px;
  text-align: right;
}

.typing-indicator {
  display: flex;
  gap: 4px;
  padding: 4px 0;
}
.typing-indicator span {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--accent-cyan);
  animation: typing-bounce 1.4s ease-in-out infinite;
}
.typing-indicator span:nth-child(2) { animation-delay: 0.2s; }
.typing-indicator span:nth-child(3) { animation-delay: 0.4s; }
@keyframes typing-bounce {
  0%, 60%, 100% { transform: translateY(0); opacity: 0.4; }
  30% { transform: translateY(-6px); opacity: 1; }
}

.chat-input-area {
  padding: 16px 24px 20px;
  border-top: 1px solid var(--border-color);
}
.input-wrapper {
  display: flex;
  gap: 10px;
  align-items: flex-end;
}
:deep(.input-wrapper .el-textarea__inner) {
  background: rgba(15, 23, 42, 0.6) !important;
  border: 1px solid var(--border-color) !important;
  border-radius: var(--border-radius-md) !important;
  color: var(--text-primary) !important;
  padding: 12px 14px !important;
}
:deep(.input-wrapper .el-textarea__inner:focus) {
  border-color: var(--accent-cyan) !important;
  box-shadow: 0 0 0 2px rgba(6, 182, 212, 0.1) !important;
}
.send-btn {
  width: 42px;
  height: 42px;
  border-radius: 12px;
  background: rgba(15, 23, 42, 0.6);
  border: 1px solid var(--border-color);
  color: var(--text-muted);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s;
  flex-shrink: 0;
  font-size: 18px;
}
.send-btn.active {
  background: var(--accent-gradient);
  border-color: transparent;
  color: white;
  box-shadow: var(--accent-glow);
}
.send-btn.active:hover {
  box-shadow: 0 6px 24px rgba(6, 182, 212, 0.5);
  transform: translateY(-2px);
}
.input-hint {
  font-size: 11px;
  color: var(--text-muted);
  margin-top: 8px;
  text-align: center;
}
</style>
