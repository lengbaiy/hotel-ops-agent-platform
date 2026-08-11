<script setup lang="ts">
import type { NavigationItem } from "../config/navigation";

defineProps<{ module: NavigationItem }>();
</script>

<template>
  <section class="module-workspace">
    <p class="eyebrow">BUSINESS MODULE</p>
    <h1>{{ module.label }}</h1>
    <p class="description">{{ module.description }}</p>
    <article class="module-card">
      <span class="status">接口契约已建立</span>
      <h2>按领域交付功能</h2>
      <p>
        后端模块：{{ module.apiModule }}。请在对应业务域补充
        Schema、应用服务、仓储、Adapter、测试和审计事件。
      </p>
      <a href="/docs" target="_blank" rel="noreferrer">查看 API 文档 →</a>
    </article>
  </section>
</template>

<style scoped>
.module-workspace {
  padding: 58px 0;
}
.eyebrow {
  margin: 0 0 8px;
  color: #2b73eb;
  font-size: 11px;
  font-weight: 800;
  letter-spacing: 1.5px;
}
.module-workspace h1 {
  margin: 0;
  font-size: 30px;
}
.description {
  color: #748198;
}
.module-card {
  max-width: 620px;
  padding: 26px;
  margin-top: 28px;
  background: #fff;
  border: 1px solid #e1e7f0;
  border-radius: 10px;
}
.module-card h2 {
  margin: 16px 0 8px;
  font-size: 18px;
}
.module-card p {
  color: #697790;
  font-size: 14px;
  line-height: 1.7;
}
.module-card a {
  color: #266de5;
  font-size: 13px;
  font-weight: 650;
  text-decoration: none;
}
.status {
  display: inline-block;
  padding: 5px 8px;
  color: #206bce;
  background: #eaf1ff;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 700;
}
</style>
