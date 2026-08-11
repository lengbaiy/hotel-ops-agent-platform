<script setup lang="ts">
import { ref } from "vue";

const task = ref<{
  id: string;
  state: string;
  recommendation?: { action: string; rationale: string };
}>();
const loading = ref(false);
const api = (path: string, method = "GET", body?: unknown) =>
  fetch(path, {
    method,
    headers: { "Content-Type": "application/json" },
    body: body ? JSON.stringify(body) : undefined,
  }).then((response) => response.json());

async function createTask() {
  loading.value = true;
  task.value = await api("/api/v2/ops/tasks", "POST", {
    tenant_id: "training",
    property_id: "hotel-demo-001",
    objective: "根据周末 Pickup 制定价格建议",
  });
  loading.value = false;
}

async function transition(action: "approve" | "execute") {
  if (task.value) task.value = await api(`/api/v2/ops/tasks/${task.value.id}/${action}`, "POST");
}
</script>

<template>
  <main>
    <header>
      <p>Hotel Operations Intelligence</p>
      <h1>经营任务中心</h1>
    </header>
    <section class="metrics">
      <article><b>OCC</b><strong>72.4%</strong></article>
      <article><b>ADR</b><strong>¥538</strong></article>
      <article><b>RevPAR</b><strong>¥390</strong></article>
      <article><b>未来 7 天 Pickup</b><strong>+18</strong></article>
    </section>
    <section class="card">
      <h2>受控策略闭环</h2>
      <p>价格、库存、预算、公开发布等写操作必须先获得审批，且执行参数不可变。</p>
      <button :disabled="loading" @click="createTask">创建模拟收益任务</button>
      <div v-if="task" class="task">
        <p><b>状态：</b>{{ task.state }}</p>
        <p v-if="task.recommendation">
          <b>建议：</b>{{ task.recommendation.action }} — {{ task.recommendation.rationale }}
        </p>
        <button v-if="task.state === 'WAITING_APPROVAL'" @click="transition('approve')">
          审批人批准
        </button>
        <button v-if="task.state === 'APPROVED'" @click="transition('execute')">
          执行模拟渠道动作
        </button>
      </div>
    </section>
  </main>
</template>

<style scoped>
:global(*) {
  box-sizing: border-box;
}
:global(body) {
  margin: 0;
  background: #f6f8fb;
  color: #172033;
  font-family: Inter, "Microsoft YaHei", sans-serif;
}
main {
  max-width: 1060px;
  margin: auto;
  padding: 52px 24px;
}
header p {
  color: #1570ef;
  font-weight: 700;
  margin: 0;
}
h1 {
  font-size: 34px;
  margin: 8px 0 32px;
}
.metrics {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 14px;
}
article,
.card {
  background: #fff;
  border: 1px solid #e5eaf1;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 3px 10px #13203808;
}
article b {
  display: block;
  color: #667085;
  font-size: 13px;
}
article strong {
  font-size: 28px;
  display: block;
  margin-top: 10px;
}
.card {
  margin-top: 24px;
}
button {
  background: #1570ef;
  color: #fff;
  border: 0;
  border-radius: 7px;
  padding: 10px 14px;
  margin: 4px 8px 4px 0;
  cursor: pointer;
}
button:disabled {
  opacity: 0.6;
}
.task {
  margin-top: 18px;
  border-left: 3px solid #1570ef;
  padding-left: 14px;
}
@media (max-width: 700px) {
  .metrics {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
