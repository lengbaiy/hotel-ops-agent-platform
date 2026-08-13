from collections.abc import Callable
from dataclasses import dataclass

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core import settings
from app.domain import OpsTask, TaskCreate

bearer_scheme = HTTPBearer(auto_error=False)
revoked_token_ids: set[str] = set()


@dataclass(frozen=True)
class Actor:
    subject: str
    tenant_id: str | None
    property_ids: frozenset[str]
    roles: frozenset[str]
    token_id: str | None = None

    def can_access_property(self, property_id: str) -> bool:
        return "*" in self.property_ids or property_id in self.property_ids


def get_current_actor(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),  # noqa: B008
) -> Actor:
    if settings.auth_mode == "disabled":
        return Actor(
            subject="local-development",
            tenant_id=None,
            property_ids=frozenset({"*"}),
            roles=frozenset({"viewer", "operator", "approver", "executor"}),
        )
    if settings.auth_mode != "jwt":
        raise RuntimeError("AUTH_MODE must be disabled or jwt")
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="bearer token required",
        )
    try:
        claims = jwt.decode(
            credentials.credentials,
            settings.jwt_secret,
            algorithms=["HS256"],
            audience=settings.jwt_audience,
        )
    except jwt.PyJWTError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid bearer token",
        ) from error
    subject = claims.get("sub")
    tenant_id = claims.get("tenant_id")
    property_ids = claims.get("property_ids", [])
    roles = claims.get("roles", [])
    token_id = claims.get("jti")
    if not isinstance(subject, str) or not isinstance(tenant_id, str):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="token subject or tenant missing",
        )
    if (
        not isinstance(property_ids, list)
        or not isinstance(roles, list)
        or not all(isinstance(value, str) for value in [*property_ids, *roles])
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="token scopes are invalid",
        )
    if not isinstance(token_id, str) or token_id in revoked_token_ids:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="session is no longer active",
        )
    return Actor(subject, tenant_id, frozenset(property_ids), frozenset(roles), token_id)


def revoke_token(actor: Actor) -> None:
    if actor.token_id:
        revoked_token_ids.add(actor.token_id)


def require_roles(*required_roles: str) -> Callable[[Actor], Actor]:
    def dependency(actor: Actor = Depends(get_current_actor)) -> Actor:  # noqa: B008
        if not actor.roles.intersection(required_roles):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="insufficient role")
        return actor

    return dependency


def authorize_task_create(actor: Actor, payload: TaskCreate) -> None:
    if actor.tenant_id is not None and payload.tenant_id != actor.tenant_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="tenant scope denied")
    if not actor.can_access_property(payload.property_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="property scope denied")


def authorize_task_access(actor: Actor, task: OpsTask) -> None:
    if actor.tenant_id is not None and task.request.tenant_id != actor.tenant_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="tenant scope denied")
    if not actor.can_access_property(task.request.property_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="property scope denied")
