export type TaskState = "PENDING" | "ANALYZING" | "WAITING_APPROVAL" | "APPROVED" | "EXECUTED" | "REJECTED";
export type TaskPriority = "CRITICAL" | "HIGH" | "MEDIUM" | "LOW";

export type TenantContext = {
  tenantId: string;
  propertyId: string;
  traceId?: string;
};

export type CreateOpsTaskRequest = TenantContext & {
  objective: string;
  taskType: string;
  priority: TaskPriority;
  ownerId?: string;
};

export type OpsTaskSummary = {
  id: string;
  state: TaskState;
  objective: string;
  priority: TaskPriority;
  ownerId?: string;
  createdAt: string;
};
