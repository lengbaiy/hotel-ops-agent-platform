# Agent Graph

`operations_graph.py` 实现 Supervisor → Specialist Agent → Policy Judge 主链路。后续在此接入 LangGraph Checkpoint、Redis 队列与人工中断恢复。Graph 只能调用只读 Tool 或提交受控执行计划，不得绕过 `policy`。
