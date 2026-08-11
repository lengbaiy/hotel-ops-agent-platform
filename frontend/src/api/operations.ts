export type MetricCard = {
  code: string;
  label: string;
  value: number;
  display_value: string;
  change_display: string;
  trend: "up" | "down" | "flat";
};

export type OperatingAlert = {
  severity: "critical" | "high" | "medium" | "low";
  title: string;
  description: string;
  module: string;
  occurred_at: string;
};

export type DashboardOverview = {
  property_id: string;
  data_cutoff: string;
  metrics: MetricCard[];
  alerts: OperatingAlert[];
  pending_approval_count: number;
};

export type OpsTask = {
  id: string;
  state: string;
  created_at: string;
  request: { objective: string; task_type: string; priority: string; owner_id?: string };
  recommendation?: { action: string; confidence: number };
};

type TaskList = { items: OpsTask[]; total: number };

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`/api/v2${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!response.ok) throw new Error(`请求失败：${response.status}`);
  return response.json() as Promise<T>;
}

export function fetchOverview(propertyId = "hotel-001") {
  return request<DashboardOverview>(`/dashboard/overview?property_id=${propertyId}`);
}

export function fetchTasks(propertyId: string) {
  return request<TaskList>(`/ops/tasks?limit=20&property_id=${propertyId}`);
}

export function createRevenueTask(propertyId: string) {
  return request<OpsTask>("/ops/tasks", {
    method: "POST",
    body: JSON.stringify({
      tenant_id: "local",
      property_id: propertyId,
      objective: "复核未来七天压缩夜的房型价格梯度与限制条件",
      task_type: "revenue_recommendation",
      priority: "HIGH",
      owner_id: "revenue-manager",
    }),
  });
}
