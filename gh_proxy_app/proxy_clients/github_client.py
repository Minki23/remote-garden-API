import httpx
from typing import Optional, Tuple


class GithubClient:
    """
    GitHub API client — handles firmware (.tar.gz) download from Releases.
    """

    def __init__(self, repo: str, token: Optional[str] = None):
        self.repo = repo
        self.token = token
        self.api_base = "https://api.github.com"

    async def _headers(self, accept: str = "application/vnd.github+json") -> dict:
        headers = {"Accept": accept}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    async def get_firmware_archive(self, version: str) -> Tuple[Optional[bytes], Optional[str]]:
        """
        Downloads firmware archive (.tar.gz) from GitHub Releases.
        Supports both 'latest' and specific tag names.
        """
        async with httpx.AsyncClient() as client:
            # handle "latest"
            if version == "latest":
                release_url = f"{self.api_base}/repos/{self.repo}/releases/latest"
            else:
                release_url = f"{self.api_base}/repos/{self.repo}/releases/tags/{version}"

            release_resp = await client.get(release_url, headers=await self._headers())

            if release_resp.status_code != 200:
                print("GitHub API error:",
                      release_resp.status_code, release_resp.text)
                return None, None

            data = release_resp.json()
            assets = data.get("assets", [])
            asset = next(
                (a for a in assets if a["name"].endswith(".tar.gz")), None)
            if not asset:
                print("No .tar.gz asset found in release:", data.get("name"))
                return None, None

            asset_api_url = asset["url"]
            print("Downloading from:", asset_api_url)

            firmware_resp = await client.get(
                asset_api_url,
                headers=await self._headers("application/octet-stream"),
                follow_redirects=True
            )

            if firmware_resp.status_code != 200:
                print("Firmware download failed:",
                      firmware_resp.status_code, firmware_resp.text)
                return None, None

            print("Firmware archive found:", asset["name"])
            return firmware_resp.content, asset["name"]
