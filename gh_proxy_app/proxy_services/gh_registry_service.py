

import base64
import logging
from typing import Optional

import httpx

logger = logging.getLogger(__name__)


class GitHubRegistryService:
    """Service handling GitHub Container Registry operations."""

    def __init__(self, github_user: str, github_token: str, ghcr_registry: str):
        self.github_user = github_user
        self.github_token = github_token
        self.ghcr_registry = ghcr_registry
        self.token_cache = {}

    async def get_registry_token(self, scope: str) -> Optional[str]:
        """Exchange GitHub PAT for GHCR registry token."""
        if scope in self.token_cache:
            return self.token_cache[scope]

        token_url = "https://ghcr.io/token"
        auth_value = base64.b64encode(
            f"{self.github_user}:{self.github_token}".encode()).decode()

        async with httpx.AsyncClient() as client:
            resp = await client.get(
                token_url,
                params={"scope": scope, "service": "ghcr.io"},
                headers={"Authorization": f"Basic {auth_value}"}
            )

            if resp.status_code == 200:
                token = resp.json().get("token")
                self.token_cache[scope] = token
                logger.info(f">>> Got GHCR token for scope: {scope}")
                return token

            logger.error(f">>> Failed to get GHCR token: {resp.status_code}")
            return None

    def get_basic_auth_header(self) -> str:
        """Get Basic Auth header with GitHub credentials."""
        auth_value = base64.b64encode(
            f"{self.github_user}:{self.github_token}".encode()).decode()
        return f"Basic {auth_value}"

    def determine_scope(self, path: str) -> Optional[str]:
        """Determine OAuth2 scope from registry path."""
        if "/" in path and ("manifests" in path or "blobs" in path):
            parts = path.split("/")
            if len(parts) >= 2:
                return f"repository:{parts[0]}/{parts[1]}:pull"
        return None
