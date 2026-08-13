<script setup lang="ts">
import { computed, ref, watch } from "vue";

import { navigationItems } from "./config/navigation";
import LoginPage from "./components/LoginPage.vue";
import { useOperationsWorkspace } from "./composables/useOperationsWorkspace";
import ModuleWorkspace from "./modules/ModuleWorkspace.vue";
import { useAuth } from "./stores/auth";

const selectedModuleId = ref(location.hash.replace("#", "") || "dashboard");
const currentModule = computed(
  () => navigationItems.find((item) => item.id === selectedModuleId.value) ?? navigationItems[0],
);
const isDashboard = computed(() => currentModule.value.id === "dashboard");
const selectedPropertyId = ref("hotel-001");
const selectedHorizon = ref("14");
const showSearch = ref(false);
const showNotifications = ref(false);
const showUserMenu = ref(false);
const searchTerm = ref("");
const properties = [
  { id: "hotel-001", name: "滨江旗舰店", description: "华东区域 · 酒店编号 H001" },
  { id: "hotel-002", name: "西湖商务店", description: "华东区域 · 酒店编号 H002" },
];
const selectedProperty = computed(
  () => properties.find((property) => property.id === selectedPropertyId.value) ?? properties[0],
);
const trendHeights = computed(() => {
  const points = {
    "7": [42, 48, 54, 50, 61, 68, 74],
    "14": [42, 48, 54, 50, 61, 68, 74, 70, 83, 78, 88, 92, 86, 90],
    "30": [
      42, 48, 54, 50, 61, 68, 74, 70, 83, 78, 88, 92, 86, 90, 84, 76, 71, 66, 62, 68, 72, 75, 80,
      85, 82, 78, 76, 79, 83, 88,
    ],
  };
  return points[selectedHorizon.value as keyof typeof points];
});
const {
  overview,
  tasks,
  pendingTasks,
  loading,
  creating,
  errorMessage,
  dataCutoff,
  loadWorkspace,
  createTask,
} = useOperationsWorkspace();
const { session, isAuthenticated, signOut } = useAuth();

watch(isAuthenticated, (authenticated) => {
  if (authenticated) loadWorkspace(selectedPropertyId.value);
});

function selectModule(moduleId: string) {
  selectedModuleId.value = moduleId;
  history.replaceState(null, "", `#${moduleId}`);
}

function changeProperty() {
  loadWorkspace(selectedPropertyId.value);
}

function openTaskCenter() {
  selectModule("tasks");
  showNotifications.value = false;
  showUserMenu.value = false;
}

function togglePanel(panel: "search" | "notifications" | "user") {
  showSearch.value = panel === "search" ? !showSearch.value : false;
  showNotifications.value = panel === "notifications" ? !showNotifications.value : false;
  showUserMenu.value = panel === "user" ? !showUserMenu.value : false;
}

function stateLabel(state: string) {
  return { WAITING_APPROVAL: "待审批", APPROVED: "已批准", EXECUTED: "已执行" }[state] ?? state;
}

async function logout() {
  await signOut();
}
</script>

<template>
  <LoginPage v-if="!isAuthenticated" />
  <div v-else class="shell">
    <aside class="sidebar">
      <div class="brand"><span class="brand-mark">H</span><span>Hotel Ops</span></div>
      <label class="property-switcher">
        <span class="property-icon">⌂</span>
        <span
          ><b>{{ selectedProperty.name }}</b
          ><small>{{ selectedProperty.description }}</small></span
        >
        <span class="property-chevron">⌄</span>
        <select v-model="selectedPropertyId" aria-label="选择门店" @change="changeProperty">
          <option v-for="property in properties" :key="property.id" :value="property.id">
            {{ property.name }}
          </option>
        </select>
      </label>
      <nav>
        <button
          v-for="item in navigationItems"
          :key="item.id"
          class="nav-item"
          :class="{ active: currentModule.id === item.id }"
          @click="selectModule(item.id)"
        >
          <span class="nav-dot"></span>{{ item.label }}
        </button>
      </nav>
      <div class="sidebar-footer">
        <span class="avatar">{{ session?.user.display_name.slice(0, 2) }}</span
        ><span
          ><b>{{ session?.user.display_name }}</b
          ><small>{{ session?.user.roles.join(" · ") }}</small></span
        ><span>⋯</span>
      </div>
    </aside>

    <main class="workspace">
      <header class="topbar">
        <div class="breadcrumb">
          经营运营 / <b>{{ currentModule.label }}</b>
        </div>
        <div class="top-actions">
          <div class="action-anchor">
            <button
              class="icon-button"
              aria-label="搜索"
              title="搜索"
              @click="togglePanel('search')"
            >
              <svg viewBox="0 0 24 24" aria-hidden="true">
                <circle cx="11" cy="11" r="6"></circle>
                <path d="m16 16 4 4"></path>
              </svg>
            </button>
            <div v-if="showSearch" class="action-popover search-popover">
              <input v-model="searchTerm" placeholder="搜索任务、门店或策略" autofocus />
              <p v-if="searchTerm">将在任务中心搜索“{{ searchTerm }}”</p>
              <p v-else>输入关键字快速定位运营对象</p>
            </div>
          </div>
          <div class="action-anchor">
            <button
              class="icon-button"
              aria-label="通知"
              title="通知"
              @click="togglePanel('notifications')"
            >
              <svg viewBox="0 0 24 24" aria-hidden="true">
                <path d="M18 9a6 6 0 0 0-12 0c0 7-3 7-3 9h18c0-2-3-2-3-9"></path>
                <path d="M10 21h4"></path>
              </svg>
            </button>
            <div v-if="showNotifications" class="action-popover notification-popover">
              <b>通知中心</b>
              <p v-if="pendingTasks.length">当前有 {{ pendingTasks.length }} 项待审批事项。</p>
              <p v-else>当前没有新的待处理通知。</p>
              <button @click="openTaskCenter">查看任务中心</button>
            </div>
          </div>
          <span class="divider"></span>
          <div class="action-anchor">
            <button class="user-button" @click="togglePanel('user')">
              {{ session?.user.display_name }} <span>⌄</span>
            </button>
            <div v-if="showUserMenu" class="action-popover user-popover">
              <b>{{ session?.user.display_name }}</b
              ><small>{{ session?.user.username }}</small
              ><button>个人设置</button><button @click="logout">退出登录</button>
            </div>
          </div>
        </div>
      </header>

      <section class="content">
        <div class="page-heading">
          <div>
            <p class="eyebrow">{{ isDashboard ? "DAILY OPERATIONS" : "BUSINESS MODULE" }}</p>
            <h1>{{ currentModule.label }}</h1>
            <p>
              {{
                isDashboard ? `数据截止：${dataCutoff} · 指标口径 V1.0` : currentModule.description
              }}
            </p>
          </div>
          <div v-if="isDashboard" class="heading-actions">
            <button
              class="secondary"
              :disabled="loading"
              @click="loadWorkspace(selectedPropertyId)"
            >
              {{ loading ? "数据加载中…" : "刷新数据" }}
            </button>
            <button class="primary" :disabled="creating" @click="createTask(selectedPropertyId)">
              + 创建经营任务
            </button>
          </div>
        </div>

        <div v-if="errorMessage" class="error-state">
          {{ errorMessage }}<button @click="loadWorkspace(selectedPropertyId)">重新加载</button>
        </div>
        <template v-else-if="isDashboard">
          <section class="metric-grid" :class="{ muted: loading }">
            <article v-for="metric in overview?.metrics" :key="metric.code" class="metric-card">
              <div class="metric-label">
                <span>{{ metric.label }}</span
                ><span class="metric-menu">•••</span>
              </div>
              <strong>{{ metric.display_value }}</strong>
              <p :class="metric.trend">
                <span>{{ metric.trend === "up" ? "↑" : "↓" }}</span
                >{{ metric.change_display }}
              </p>
            </article>
          </section>

          <section class="dashboard-grid">
            <article class="panel performance-panel">
              <div class="panel-heading">
                <div>
                  <h2>未来 {{ selectedHorizon }} 天经营趋势</h2>
                  <p>基于 Pickup、库存与预算口径</p>
                </div>
                <select v-model="selectedHorizon" class="select-button" aria-label="选择趋势周期">
                  <option value="7">未来 7 天</option>
                  <option value="14">未来 14 天</option>
                  <option value="30">未来 30 天</option>
                </select>
              </div>
              <div class="chart-area">
                <div class="chart-y">
                  <span>100%</span><span>75%</span><span>50%</span><span>25%</span><span>0%</span>
                </div>
                <div class="bars">
                  <i
                    v-for="(height, index) in trendHeights"
                    :key="`${selectedHorizon}-${index}`"
                    :style="{ height: `${height}%` }"
                  ></i>
                </div>
              </div>
              <div class="chart-legend">
                <span><i class="legend-dot blue"></i>预测入住率</span
                ><span><i class="legend-dot teal"></i>预算达成</span>
              </div>
            </article>

            <article class="panel approval-panel">
              <div class="panel-heading">
                <div>
                  <h2>待审批事项</h2>
                  <p>{{ pendingTasks.length }} 项需要处理</p>
                </div>
                <button class="link-button" @click="openTaskCenter">查看全部 →</button>
              </div>
              <div v-if="!pendingTasks.length" class="empty-approval">当前没有待审批事项</div>
              <div v-for="task in pendingTasks.slice(0, 3)" :key="task.id" class="approval-item">
                <span class="approval-icon">¥</span>
                <div>
                  <b>{{ task.request.objective }}</b>
                  <p>{{ task.request.task_type }} · {{ task.request.priority }}</p>
                </div>
                <span class="status waiting">{{ stateLabel(task.state) }}</span>
              </div>
            </article>
          </section>

          <section class="dashboard-grid bottom-grid">
            <article class="panel tasks-panel">
              <div class="panel-heading">
                <div>
                  <h2>经营任务</h2>
                  <p>策略、异常、审批与复盘统一追踪</p>
                </div>
                <button class="link-button" @click="openTaskCenter">任务中心 →</button>
              </div>
              <div class="task-table">
                <div class="table-head">
                  <span>任务</span><span>模块</span><span>优先级</span><span>状态</span>
                </div>
                <div v-if="!tasks.length" class="empty-row">暂无任务，可从“创建经营任务”开始。</div>
                <div v-for="task in tasks" :key="task.id" class="table-row">
                  <span
                    ><b>{{ task.request.objective }}</b
                    ><small
                      >{{ task.id.slice(0, 8) }} · {{ task.request.owner_id ?? "未分配" }}</small
                    ></span
                  ><span>收益管理</span
                  ><span><i class="priority-dot"></i>{{ task.request.priority }}</span
                  ><span class="status waiting">{{ stateLabel(task.state) }}</span>
                </div>
              </div>
            </article>
            <article class="panel alerts-panel">
              <div class="panel-heading">
                <div>
                  <h2>经营预警</h2>
                  <p>市场、渠道、事件与执行风险</p>
                </div>
                <button class="link-button">全部预警 →</button>
              </div>
              <div v-for="alert in overview?.alerts" :key="alert.title" class="alert-item">
                <i :class="alert.severity"></i>
                <div>
                  <b>{{ alert.title }}</b>
                  <p>{{ alert.description }}</p>
                  <small>{{ alert.module }} · 刚刚更新</small>
                </div>
              </div>
            </article>
          </section>
        </template>
        <ModuleWorkspace v-else :module="currentModule" />
      </section>
    </main>
  </div>
</template>

<style scoped>
:global(*) {
  box-sizing: border-box;
}
:global(body) {
  margin: 0;
  min-width: 1180px;
  color: #17233b;
  background: #f6f8fc;
  font-family: Inter, "Microsoft YaHei", sans-serif;
}
button {
  font: inherit;
  cursor: pointer;
}
.shell {
  display: flex;
  min-height: 100vh;
}
.sidebar {
  width: 244px;
  padding: 24px 14px 16px;
  color: #b8c2d7;
  background: #111b31;
  display: flex;
  flex-direction: column;
}
.brand {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 0 12px 26px;
  font-size: 19px;
  font-weight: 750;
  color: #fff;
}
.brand-mark {
  display: grid;
  width: 29px;
  height: 29px;
  color: #111b31;
  background: #4ed1c5;
  place-items: center;
  border-radius: 8px;
}
.property-switcher {
  position: relative;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 13px;
  color: #fff;
  background: #1d2a46;
  border: 1px solid #2a3959;
  border-radius: 8px;
  font-size: 12px;
}
.property-switcher span:nth-child(2) {
  flex: 1;
}
.property-chevron {
  color: #d9e2f2;
  font-size: 15px;
}
.property-switcher b,
.sidebar-footer b {
  display: block;
  font-size: 13px;
}
.property-switcher small,
.sidebar-footer small {
  display: block;
  margin-top: 4px;
  color: #8e9ab1;
  font-size: 11px;
}
.property-switcher select {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  opacity: 0;
  cursor: pointer;
}
nav {
  margin-top: 24px;
}
.nav-item {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 11px 13px;
  color: #b8c2d7;
  background: transparent;
  border: 0;
  border-radius: 7px;
  text-align: left;
  font-size: 14px;
}
.nav-item:hover,
.nav-item.active {
  color: #fff;
  background: #243455;
}
.nav-item.active {
  box-shadow: inset 3px 0 #4ed1c5;
}
.nav-dot {
  width: 7px;
  height: 7px;
  background: #8090af;
  border-radius: 50%;
}
.nav-item.active .nav-dot {
  background: #4ed1c5;
}
.sidebar-footer {
  margin-top: auto;
  display: flex;
  align-items: center;
  gap: 9px;
  padding: 12px;
  border-top: 1px solid #293653;
  font-size: 12px;
}
.sidebar-footer span:nth-child(2) {
  flex: 1;
}
.avatar {
  display: grid;
  width: 31px;
  height: 31px;
  color: #142039;
  background: #e7b77b;
  border-radius: 50%;
  place-items: center;
  font-size: 10px;
  font-weight: 700;
}
.workspace {
  flex: 1;
}
.topbar {
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 34px;
  background: #fff;
  border-bottom: 1px solid #e5eaf2;
  font-size: 13px;
}
.breadcrumb {
  color: #7e8aa0;
}
.breadcrumb b {
  color: #34415a;
}
.top-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}
.action-anchor {
  position: relative;
}
.icon-button,
.user-button {
  color: #53617a;
  background: transparent;
  border: 0;
}
.icon-button {
  display: grid;
  width: 32px;
  height: 32px;
  padding: 0;
  place-items: center;
  border-radius: 6px;
}
.icon-button:hover,
.user-button:hover {
  background: #f2f5fa;
}
.icon-button svg {
  width: 18px;
  height: 18px;
  fill: none;
  stroke: currentcolor;
  stroke-linecap: round;
  stroke-linejoin: round;
  stroke-width: 1.8;
}
.user-button {
  padding: 8px 10px;
  border-radius: 6px;
}
.action-popover {
  position: absolute;
  z-index: 20;
  top: 40px;
  right: 0;
  width: 250px;
  padding: 14px;
  color: #33415b;
  background: #fff;
  border: 1px solid #dfe6f0;
  border-radius: 8px;
  box-shadow: 0 12px 28px #182a481f;
  font-size: 12px;
}
.action-popover p {
  margin: 10px 0;
  color: #718098;
  line-height: 1.5;
}
.action-popover input {
  width: 100%;
  padding: 9px 10px;
  border: 1px solid #d9e1ed;
  border-radius: 6px;
  outline: none;
}
.action-popover input:focus {
  border-color: #2c71e8;
}
.action-popover button {
  width: 100%;
  padding: 8px 0;
  color: #286fe5;
  background: transparent;
  border: 0;
  text-align: left;
}
.user-popover {
  display: flex;
  flex-direction: column;
  gap: 3px;
}
.user-popover small {
  padding-bottom: 10px;
  color: #8a96a9;
  border-bottom: 1px solid #edf1f5;
}
.divider {
  width: 1px;
  height: 20px;
  background: #e0e6ee;
}
.content {
  max-width: 1500px;
  padding: 32px 38px 42px;
  margin: 0 auto;
}
.page-heading {
  display: flex;
  align-items: end;
  justify-content: space-between;
  margin-bottom: 26px;
}
.eyebrow {
  margin: 0 0 7px;
  color: #2b73eb;
  font-size: 11px;
  font-weight: 800;
  letter-spacing: 1.5px;
}
.page-heading h1 {
  margin: 0;
  color: #14223c;
  font-size: 28px;
}
.page-heading p:not(.eyebrow) {
  margin: 9px 0 0;
  color: #748198;
  font-size: 13px;
}
.heading-actions {
  display: flex;
  gap: 10px;
}
.primary,
.secondary {
  padding: 10px 15px;
  border-radius: 7px;
  font-weight: 650;
  font-size: 13px;
}
.primary {
  color: #fff;
  background: #246ee9;
  border: 1px solid #246ee9;
}
.primary:disabled {
  opacity: 0.6;
}
.secondary {
  color: #3d4b65;
  background: #fff;
  border: 1px solid #d9e0ea;
}
.metric-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 17px;
}
.metric-grid.muted {
  opacity: 0.55;
}
.metric-card,
.panel {
  background: #fff;
  border: 1px solid #e1e7f0;
  border-radius: 10px;
  box-shadow: 0 2px 7px #1c2e4d08;
}
.metric-card {
  padding: 19px 20px;
}
.metric-label {
  display: flex;
  justify-content: space-between;
  color: #65738c;
  font-size: 13px;
}
.metric-menu {
  color: #aab4c4;
}
.metric-card strong {
  display: block;
  margin: 12px 0 7px;
  color: #15233e;
  font-size: 28px;
}
.metric-card p {
  margin: 0;
  font-size: 12px;
  font-weight: 600;
}
.metric-card p.up {
  color: #15957d;
}
.metric-card p.down {
  color: #d6525c;
}
.metric-card p span {
  margin-right: 4px;
}
.dashboard-grid {
  display: grid;
  grid-template-columns: 1.5fr 1fr;
  gap: 17px;
}
.bottom-grid {
  margin-top: 17px;
  grid-template-columns: 1.5fr 1fr;
}
.panel {
  padding: 21px;
}
.panel-heading {
  display: flex;
  align-items: start;
  justify-content: space-between;
}
.panel h2 {
  margin: 0;
  font-size: 16px;
}
.panel-heading p {
  margin: 6px 0 0;
  color: #7b889d;
  font-size: 12px;
}
.select-button {
  padding: 7px 10px;
  color: #526079;
  background: #fff;
  border: 1px solid #dce3ec;
  border-radius: 6px;
  font-size: 12px;
}
.link-button {
  padding: 2px;
  color: #266de5;
  background: transparent;
  border: 0;
  font-size: 12px;
  font-weight: 650;
}
.chart-area {
  display: flex;
  height: 206px;
  margin: 21px 0 8px;
}
.chart-y {
  display: flex;
  width: 38px;
  flex-direction: column;
  justify-content: space-between;
  color: #95a2b5;
  font-size: 10px;
}
.bars {
  display: flex;
  flex: 1;
  align-items: end;
  gap: 10px;
  padding: 0 10px;
  border-bottom: 1px solid #e3e8ef;
  background: repeating-linear-gradient(to bottom, transparent 0, transparent 50px, #f0f3f8 51px);
}
.bars i {
  flex: 1;
  min-width: 9px;
  background: linear-gradient(#6a9ef2, #2d72e9);
  border-radius: 4px 4px 0 0;
  opacity: 0.9;
}
.bars i:nth-child(3n) {
  background: linear-gradient(#55d0c5, #1aa896);
}
.chart-legend {
  display: flex;
  gap: 20px;
  padding-left: 40px;
  color: #76839a;
  font-size: 11px;
}
.legend-dot {
  display: inline-block;
  width: 7px;
  height: 7px;
  margin-right: 5px;
  border-radius: 50%;
}
.blue {
  background: #2d72e9;
}
.teal {
  background: #1aa896;
}
.approval-item {
  display: flex;
  align-items: center;
  gap: 11px;
  padding: 15px 0;
  border-bottom: 1px solid #edf0f5;
}
.approval-item:last-child {
  border: 0;
}
.approval-icon {
  display: grid;
  flex: 0 0 auto;
  width: 30px;
  height: 30px;
  color: #2169dd;
  background: #eaf1ff;
  border-radius: 7px;
  place-items: center;
  font-weight: 700;
}
.approval-icon.orange {
  color: #d77827;
  background: #fff1e4;
}
.approval-icon.purple {
  color: #835ad6;
  background: #f1eaff;
}
.approval-item div {
  flex: 1;
}
.approval-item b,
.alert-item b {
  font-size: 13px;
}
.approval-item p {
  margin: 4px 0 0;
  color: #8490a3;
  font-size: 11px;
}
.status {
  display: inline-flex;
  width: fit-content;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 650;
}
.waiting {
  color: #a76a13;
  background: #fff4dc;
}
.task-table {
  margin-top: 18px;
}
.table-head,
.table-row {
  display: grid;
  grid-template-columns: 2.4fr 1fr 0.8fr 0.7fr;
  gap: 10px;
  align-items: center;
}
.table-head {
  padding: 9px 10px;
  color: #8793a8;
  background: #f7f9fc;
  font-size: 11px;
}
.table-row {
  padding: 14px 10px;
  color: #58667e;
  border-bottom: 1px solid #edf0f5;
  font-size: 12px;
}
.table-row b {
  display: block;
  overflow: hidden;
  color: #2e3d56;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 12px;
}
.table-row small {
  display: block;
  margin-top: 4px;
  color: #97a2b3;
  font-size: 10px;
}
.priority-dot {
  display: inline-block;
  width: 6px;
  height: 6px;
  margin-right: 5px;
  background: #e68e3e;
  border-radius: 50%;
}
.empty-row {
  padding: 28px 10px;
  color: #8d99aa;
  text-align: center;
  font-size: 13px;
}
.alert-item {
  display: flex;
  gap: 11px;
  padding: 15px 0;
  border-bottom: 1px solid #edf0f5;
}
.alert-item:last-child {
  border: 0;
}
.alert-item > i {
  width: 8px;
  height: 8px;
  margin-top: 5px;
  border-radius: 50%;
}
.alert-item > i.high {
  background: #e7686c;
}
.alert-item > i.medium {
  background: #e8aa45;
}
.alert-item p {
  margin: 5px 0;
  color: #76849a;
  font-size: 12px;
  line-height: 1.5;
}
.alert-item small {
  color: #9aa5b5;
  font-size: 10px;
}
.error-state {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 15px 18px;
  margin-bottom: 17px;
  color: #a23b42;
  background: #fff0f1;
  border: 1px solid #ffd8db;
  border-radius: 8px;
  font-size: 13px;
}
.error-state button {
  color: #a23b42;
  background: transparent;
  border: 0;
  text-decoration: underline;
}
.empty-approval {
  padding: 42px 0;
  color: #8d99aa;
  text-align: center;
  font-size: 13px;
}
</style>
