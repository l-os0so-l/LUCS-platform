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
            <div
              class="message-content"
              :class="{ 'md-content': msg.role === 'ai' }"
              v-html="msg.role === 'ai' ? marked.parse(msg.content) : msg.content"
            />
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
            <div v-if="showThinkingHint" class="thinking-hint">
              正在努力思考中，请稍候…
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
import { chatWithAI } from "../api/qa";
import { ElMessage } from "element-plus";
import { marked } from "marked";

const question = ref("");
const sending = ref(false);
const isTyping = ref(false);
const showThinkingHint = ref(false);
const messagesRef = ref(null);
let thinkingTimer = null;

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
  showThinkingHint.value = false;
  scrollToBottom();

  isTyping.value = true;
  scrollToBottom();

  // 8 秒后显示思考提示
  thinkingTimer = setTimeout(() => {
    if (isTyping.value) {
      showThinkingHint.value = true;
    }
  }, 8000);

  try {
    const res = await chatWithAI({ message: text });
    clearTimeout(thinkingTimer);
    showThinkingHint.value = false;
    isTyping.value = false;
    if (res.success && res.data) {
      messages.value.push({
        role: "ai",
        content: res.data.reply,
        time: getCurrentTime(),
      });
    } else {
      messages.value.push({
        role: "ai",
        content: "抱歉，服务暂时不可用，请稍后再试。",
        time: getCurrentTime(),
      });
    }
  } catch (error) {
    clearTimeout(thinkingTimer);
    showThinkingHint.value = false;
    isTyping.value = false;
    const msg = error.response?.data?.detail || error.message || "请求失败";
    messages.value.push({
      role: "ai",
      content: `抱歉，${msg}`,
      time: getCurrentTime(),
    });
  }

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
  gap: 10px;
  margin-bottom: 8px;
}
.page-title {
  font-size: 18px;
  font-weight: 700;
  margin: 0;
}
.page-subtitle {
  font-size: 12px;
  color: var(--text-muted);
  margin: 2px 0 0;
}
.header-icon-wrap {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  background: var(--accent-gradient);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 18px;
  box-shadow: var(--accent-glow);
  flex-shrink: 0;
}

.quick-tags {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
  margin-bottom: 10px;
}
.quick-label {
  font-size: 12px;
  color: var(--text-muted);
}
.quick-tag {
  padding: 4px 10px;
  background: rgba(6, 182, 212, 0.08);
  border: 1px solid rgba(6, 182, 212, 0.2);
  border-radius: 16px;
  color: var(--accent-cyan);
  font-size: 11px;
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
  padding: 16px 20px;
  overflow-y: auto;
  min-height: 0;
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
  word-break: break-word;
}

/* Markdown 样式 */
.md-content :deep(h1),
.md-content :deep(h2),
.md-content :deep(h3),
.md-content :deep(h4) {
  margin: 12px 0 8px;
  color: var(--text-heading);
  font-weight: 600;
}
.md-content :deep(p) {
  margin: 6px 0;
}
.md-content :deep(ul),
.md-content :deep(ol) {
  margin: 6px 0;
  padding-left: 20px;
}
.md-content :deep(li) {
  margin: 3px 0;
}
.md-content :deep(strong) {
  color: var(--text-heading);
  font-weight: 600;
}
.md-content :deep(code) {
  background: rgba(6, 182, 212, 0.1);
  padding: 2px 6px;
  border-radius: 4px;
  font-family: monospace;
  font-size: 13px;
  color: var(--accent-cyan);
}
.md-content :deep(pre) {
  background: rgba(15, 23, 42, 0.8);
  padding: 12px;
  border-radius: 8px;
  overflow-x: auto;
  margin: 8px 0;
  border: 1px solid var(--border-color);
}
.md-content :deep(pre code) {
  background: transparent;
  padding: 0;
  color: var(--text-secondary);
}
.md-content :deep(blockquote) {
  margin: 8px 0;
  padding-left: 12px;
  border-left: 3px solid var(--accent-cyan);
  color: var(--text-muted);
}
.md-content :deep(a) {
  color: var(--accent-cyan);
  text-decoration: none;
}
.md-content :deep(a:hover) {
  text-decoration: underline;
}
.md-content :deep(table) {
  width: 100%;
  border-collapse: collapse;
  margin: 8px 0;
  font-size: 13px;
}
.md-content :deep(th),
.md-content :deep(td) {
  padding: 6px 10px;
  border: 1px solid var(--border-color);
  text-align: left;
}
.md-content :deep(th) {
  background: rgba(6, 182, 212, 0.08);
  font-weight: 600;
  color: var(--text-heading);
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

.thinking-hint {
  font-size: 12px;
  color: var(--text-muted);
  margin-top: 8px;
  animation: fadeIn 0.4s ease;
}
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
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
