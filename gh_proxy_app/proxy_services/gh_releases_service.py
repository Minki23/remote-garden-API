import os
import logging
from typing import Optional, Tuple

import httpx

logger = logging.getLogger(__name__)


class GitHubReleasesService:
    """Service handling GitHub Releases operations."""

    def __init__(self, github_repo: str, github_token: str):
        self.github_repo = github_repo
        self.github_token = github_token
        self.github_api_base_url = os.getenv("GITHUB_API_BASE_URL", "https://api.github.com")
        self.github_api_version = os.getenv("GITHUB_API_VERSION", "2022-11-28")
        self.http_follow_redirects = os.getenv("HTTP_FOLLOW_REDIRECTS", "true").lower() == "true"
        self.firmware_extensions = os.getenv("FIRMWARE_ASSET_EXTENSIONS", ".tar.gz,.zip,.bin,.gz").split(",")

    async def get_firmware_archive(self, version: str) -> Tuple[Optional[bytes], Optional[str]]:
        """Download firmware archive from GitHub releases."""
        if version.lower() == "latest":
            url = f"{self.github_api_base_url}/repos/{self.github_repo}/releases/latest"
        else:
            url = f"{self.github_api_base_url}/repos/{self.github_repo}/releases/tags/{version}"

        headers = {
            "Authorization": f"Bearer {self.github_token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": self.github_api_version
        }

        async with httpx.AsyncClient(follow_redirects=self.http_follow_redirects) as client:
            resp = await client.get(url, headers=headers)
            if resp.status_code != 200:
                logger.error(
                    f"Failed to get release info: {resp.status_code} - {resp.text}")
                return None, None

            release = resp.json()

            firmware_asset = self._find_firmware_asset(
                release.get("assets", []))
            if not firmware_asset:
                logger.error("No firmware asset found in release")
                return None, None

            return await self._download_asset(firmware_asset, headers)

    def _find_firmware_asset(self, assets: list) -> Optional[dict]:
        """Find firmware asset in release assets."""
        for asset in assets:
            if any(asset["name"].endswith(ext.strip()) for ext in self.firmware_extensions):
                return asset
        return None

    async def _download_asset(self, asset: dict, base_headers: dict) -> Tuple[Optional[bytes], Optional[str]]:
        """Download asset from GitHub."""
        asset_url = asset["url"]
        filename = asset["name"]

        headers = base_headers.copy()
        headers["Accept"] = "application/octet-stream"

        async with httpx.AsyncClient(follow_redirects=self.http_follow_redirects) as client:
            resp = await client.get(asset_url, headers=headers)

            if resp.status_code != 200:
                logger.error(
                    f"Failed to download firmware: {resp.status_code} - {resp.text}")
                return None, None

            return resp.content, filename