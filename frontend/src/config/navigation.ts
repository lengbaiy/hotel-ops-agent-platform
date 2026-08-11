export type NavigationItem = {
  id: string;
  label: string;
  description: string;
  apiModule: string;
};

export const navigationItems: NavigationItem[] = [
  {
    id: "dashboard",
    label: "经营总览",
    description: "经营指标、预警与审批概览",
    apiModule: "dashboard",
  },
  { id: "tasks", label: "任务中心", description: "分析、策略、审批与复盘任务", apiModule: "ops" },
  {
    id: "market",
    label: "市场情报",
    description: "同行、事件、活动与证据快照",
    apiModule: "market_intelligence",
  },
  {
    id: "forecast",
    label: "需求预测",
    description: "120 天需求、Pickup 与压缩夜",
    apiModule: "demand_forecast",
  },
  {
    id: "revenue",
    label: "收益管理",
    description: "价格、库存、限制条件与净 ADR",
    apiModule: "revenue_management",
  },
  {
    id: "channel",
    label: "渠道运营",
    description: "价盘、库存、活动与贡献利润",
    apiModule: "channel_operations",
  },
  {
    id: "content",
    label: "内容增长",
    description: "选题、素材、审核与授权发布",
    apiModule: "content_growth",
  },
  {
    id: "reputation",
    label: "口碑与会员",
    description: "评论闭环、合规分群与触达",
    apiModule: "reputation_membership",
  },
  {
    id: "knowledge",
    label: "知识与评测",
    description: "运营知识、评测集与归因复盘",
    apiModule: "knowledge_measurement",
  },
  {
    id: "system",
    label: "系统管理",
    description: "数据源、权限、规则与可观测性",
    apiModule: "platform",
  },
];
