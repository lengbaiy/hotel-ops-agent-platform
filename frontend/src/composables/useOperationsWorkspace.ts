import { computed, onMounted, ref } from "vue";

import {
  createRevenueTask,
  fetchOverview,
  fetchTasks,
  type DashboardOverview,
  type OpsTask,
} from "../api/operations";

export function useOperationsWorkspace() {
  const overview = ref<DashboardOverview>();
  const tasks = ref<OpsTask[]>([]);
  const loading = ref(true);
  const creating = ref(false);
  const errorMessage = ref("");
  const pendingTasks = computed(() =>
    tasks.value.filter((task) => task.state === "WAITING_APPROVAL"),
  );
  const dataCutoff = computed(() => {
    if (!overview.value) return "--";
    return new Intl.DateTimeFormat("zh-CN", { dateStyle: "medium", timeStyle: "short" }).format(
      new Date(overview.value.data_cutoff),
    );
  });

  async function loadWorkspace(propertyId = "hotel-001") {
    loading.value = true;
    errorMessage.value = "";
    try {
      const [overviewData, taskData] = await Promise.all([
        fetchOverview(propertyId),
        fetchTasks(propertyId),
      ]);
      overview.value = overviewData;
      tasks.value = taskData.items;
    } catch (error) {
      errorMessage.value = error instanceof Error ? error.message : "无法加载运营数据";
    } finally {
      loading.value = false;
    }
  }

  async function createTask(propertyId = "hotel-001") {
    creating.value = true;
    try {
      await createRevenueTask(propertyId);
      await loadWorkspace(propertyId);
    } catch (error) {
      errorMessage.value = error instanceof Error ? error.message : "创建任务失败";
    } finally {
      creating.value = false;
    }
  }

  onMounted(loadWorkspace);
  return {
    overview,
    tasks,
    pendingTasks,
    loading,
    creating,
    errorMessage,
    dataCutoff,
    loadWorkspace,
    createTask,
  };
}
