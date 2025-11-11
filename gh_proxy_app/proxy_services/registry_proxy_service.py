import os
import logging
from typing import Optional
from urllib.parse import unquote
from fastapi import Request, Response
import httpx
from proxy_services.gh_registry_service import GitHubRegistryService

logger = logging.getLogger(__name__)


class RegistryProxyService:
    """Service handling Docker registry proxy operations."""

    def __init__(self, registry_service: GitHubRegistryService):
        self.registry_service = registry_service
        self.http_timeout = float(os.getenv("HTTP_TIMEOUT", "60.0"))
        self.docker_api_version = os.getenv("DOCKER_API_VERSION", "registry/2.0")
        self.basic_auth_realm = os.getenv("BASIC_AUTH_REALM", "Docker Registry")

    def create_unauthorized_response(self) -> Response:
        """Create 401 Unauthorized response with Docker headers."""
        return Response(
            status_code=401,
            headers={
                "Docker-Distribution-API-Version": self.docker_api_version,
                "WWW-Authenticate": f'Basic realm="{self.basic_auth_realm}"'
            }
        )

    def create_success_response(self) -> Response:
        """Create 200 OK response with Docker headers."""
        return Response(
            status_code=200,
            headers={"Docker-Distribution-API-Version": self.docker_api_version}
        )

    async def proxy_request(self, request: Request, path: str) -> Response:
        """Proxy request to GHCR."""
        decoded_path = unquote(path)
        target_url = f"{self.registry_service.ghcr_registry}/v2/{decoded_path}"

        scope = self.registry_service.determine_scope(decoded_path)
        headers = await self._prepare_headers(request, scope)

        if headers is None:
            return Response(status_code=500, content=b"Failed to authenticate with GHCR")

        body = await request.body() if request.method not in ["GET", "HEAD"] else None

        async with httpx.AsyncClient() as client:
            resp = await client.request(
                method=request.method,
                url=target_url,
                headers=headers,
                params=request.query_params,
                content=body,
                timeout=self.http_timeout,
            )

        logger.info(f">>> {request.method} /{path} -> {resp.status_code}")

        filtered_headers = {
            k: v for k, v in resp.headers.items()
            if k.lower() not in ["content-encoding", "transfer-encoding", "connection"]
        }

        return Response(
            content=resp.content,
            status_code=resp.status_code,
            headers=filtered_headers
        )

    async def _prepare_headers(self, request: Request, scope: Optional[str]) -> Optional[dict]:
        """Prepare headers for GHCR request."""
        headers = dict(request.headers)
        headers.pop("host", None)
        headers.pop("authorization", None)

        if scope:
            ghcr_token = await self.registry_service.get_registry_token(scope)
            if ghcr_token:
                headers["Authorization"] = f"Bearer {ghcr_token}"
            else:
                return None
        else:
            headers["Authorization"] = self.registry_service.get_basic_auth_header()

        return headers