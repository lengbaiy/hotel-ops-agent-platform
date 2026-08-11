from dataclasses import dataclass

from app.domain import Recommendation, TaskCreate


@dataclass(frozen=True)
class SpecialistProfile:
    name: str
    action: str
    rationale: str
    parameters: dict[str, str | int | float]


class RuleBasedSpecialistAgent:
    """专项 Agent 的结构化基线；后续可在保留输出契约前提下替换为模型节点。"""

    def __init__(self, profile: SpecialistProfile) -> None:
        self.profile = profile
        self.name = profile.name

    def recommend(self, task: TaskCreate) -> Recommendation:
        return Recommendation(
            action=self.profile.action,
            parameters=self.profile.parameters,
            rationale=f"{self.profile.rationale} 任务目标：{task.objective}",
            confidence=0.65,
            evidence_refs=[f"pending://{self.name}/evidence"],
        )
