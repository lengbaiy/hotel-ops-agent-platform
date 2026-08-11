from fastapi import APIRouter, HTTPException

router = APIRouter(tags=["platform"])

CAPABILITIES = {
    "market_rate_shop": "market_intelligence",
    "market_events": "demand_forecast",
    "demand_forecast": "demand_forecast",
    "revenue_recommendations": "revenue_management",
    "approvals": "strategy_governance",
    "executions": "strategy_governance",
    "content_generation": "content_growth",
    "content_publish": "content_growth",
    "measurements": "knowledge_measurement",
    "knowledge_search": "knowledge_measurement",
}


@router.get("/platform/capabilities")
def list_capabilities() -> dict[str, dict[str, str]]:
    capabilities: dict[str, dict[str, str]] = {}
    for name, module in CAPABILITIES.items():
        capabilities[name] = {"module": module, "status": "SCAFFOLDED"}
    return capabilities


@router.post("/market/rate-shop", status_code=501)
@router.get("/market/events", status_code=501)
@router.post("/forecast/demand", status_code=501)
@router.post("/revenue/recommendations", status_code=501)
@router.post("/approvals", status_code=501)
@router.post("/executions", status_code=501)
@router.post("/content/generate", status_code=501)
@router.post("/content/publish", status_code=501)
@router.get("/measurements/{measurement_id}", status_code=501)
@router.post("/knowledge/search", status_code=501)
def planned_capability(measurement_id: str | None = None) -> None:
    raise HTTPException(
        status_code=501,
        detail=(
            "Capability contract is scaffolded. "
            "Implement the corresponding business module before enabling it."
        ),
    )
