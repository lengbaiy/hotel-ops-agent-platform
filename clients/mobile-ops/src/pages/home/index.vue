<script setup lang="ts">
const metrics = [
  { label: "入住率", value: "72.4%" },
  { label: "RevPAR", value: "¥390" },
  { label: "待审批", value: "0" },
];
</script>

<template>
  <view class="page">
    <view class="header"><text class="eyebrow">HOTEL OPS</text><text class="title">今日经营</text><text class="subtitle">滨江旗舰店 · 数据截止 08:30</text></view>
    <view class="metric-grid"><view v-for="metric in metrics" :key="metric.label" class="metric-card"><text>{{ metric.label }}</text><strong>{{ metric.value }}</strong></view></view>
    <view class="section"><view class="section-title"><text>待处理事项</text><navigator url="/pages/tasks/index">全部 →</navigator></view><view class="empty">当前没有待审批事项</view></view>
  </view>
</template>

<style scoped>
.page { padding: 32rpx; }.header { display: flex; flex-direction: column; gap: 10rpx; }.eyebrow { color: #2670e8; font-size: 22rpx; font-weight: 700; letter-spacing: 2rpx; }.title { font-size: 48rpx; font-weight: 700; }.subtitle { color: #77859d; font-size: 25rpx; }.metric-grid { display: flex; gap: 18rpx; margin: 34rpx 0; }.metric-card { flex: 1; display: flex; flex-direction: column; gap: 16rpx; padding: 24rpx; background: #fff; border-radius: 16rpx; color: #748198; font-size: 24rpx; }.metric-card strong { color: #15233e; font-size: 34rpx; }.section { padding: 28rpx; background: #fff; border-radius: 16rpx; }.section-title { display: flex; justify-content: space-between; font-weight: 700; }.section-title navigator { color: #2670e8; font-size: 25rpx; }.empty { padding: 48rpx 0 20rpx; color: #8d99aa; text-align: center; font-size: 26rpx; }
</style>
