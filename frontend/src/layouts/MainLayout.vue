<template>
  <div class="main-layout">
    <!-- 动态背景层 -->
    <div class="ambient-bg">
      <div class="orb orb-1"></div>
      <div class="orb orb-2"></div>
      <div class="orb orb-3"></div>
      <div class="grid-overlay"></div>
    </div>

    <aside class="sidebar">
      <slot name="sidebar"></slot>
    </aside>

    <div class="main-container">
      <header class="header">
        <slot name="header"></slot>
      </header>

      <main class="content">
        <slot name="content"></slot>
      </main>
    </div>
  </div>
</template>

<script setup></script>

<style scoped>
.main-layout {
  display: flex;
  height: 100vh;
  overflow: hidden;
  position: relative;
  background: var(--bg-primary);
}

/* 动态环境背景 */
.ambient-bg {
  position: fixed;
  inset: 0;
  z-index: 0;
  pointer-events: none;
  overflow: hidden;
}

.orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  opacity: 0.15;
  animation: orb-float 20s ease-in-out infinite;
}
.orb-1 {
  width: 600px;
  height: 600px;
  background: var(--accent-cyan);
  top: -200px;
  right: -100px;
  animation-delay: 0s;
}
.orb-2 {
  width: 500px;
  height: 500px;
  background: var(--accent-purple);
  bottom: -150px;
  left: 20%;
  animation-delay: -7s;
}
.orb-3 {
  width: 400px;
  height: 400px;
  background: var(--accent-pink);
  top: 40%;
  right: 10%;
  animation-delay: -14s;
}

@keyframes orb-float {
  0%, 100% {
    transform: translate(0, 0) scale(1);
  }
  33% {
    transform: translate(30px, -40px) scale(1.1);
  }
  66% {
    transform: translate(-20px, 30px) scale(0.95);
  }
}

/* 网格纹理覆盖 */
.grid-overlay {
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(rgba(99, 102, 241, 0.03) 1px, transparent 1px),
    linear-gradient(90deg, rgba(99, 102, 241, 0.03) 1px, transparent 1px);
  background-size: 60px 60px;
  mask-image: radial-gradient(ellipse at center, black 30%, transparent 70%);
  -webkit-mask-image: radial-gradient(ellipse at center, black 30%, transparent 70%);
}

.sidebar {
  width: 240px;
  flex-shrink: 0;
  background: rgba(6, 10, 20, 0.85);
  backdrop-filter: blur(20px);
  border-right: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
  z-index: 10;
  position: relative;
}

.main-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  position: relative;
  z-index: 1;
}

.header {
  height: 68px;
  background: rgba(6, 10, 20, 0.6);
  backdrop-filter: blur(16px);
  border-bottom: 1px solid var(--border-color);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 28px;
  z-index: 5;
  position: relative;
}

.content {
  flex: 1;
  padding: 28px 32px;
  overflow-y: auto;
  position: relative;
  z-index: 1;
}

/* 响应式 */
@media (max-width: 768px) {
  .sidebar {
    width: 0;
    overflow: hidden;
  }
  .content {
    padding: 20px 16px;
  }
}
</style>
