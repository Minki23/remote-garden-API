import os
from fastapi import FastAPI, Request, Response, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import logging

from proxy_services.auth_service import ProxyAuthService
from proxy_services.gh_registry_service import GitHubRegistryService
from proxy_services.gh_releases_service import GitHubReleasesService
from proxy_services.registry_proxy_service import RegistryProxyService

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


app = FastAPI(title="GitHub Registry Proxy & Firmware Server")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_USER = os.getenv("GITHUB_USER", "filxxip")
GITHUB_REPO = os.getenv("GITHUB_REPO", "filxxip/remote-garden-ESP")
GHCR_REGISTRY = "https://ghcr.io"
AUTH_API_URL = os.getenv("AUTH_API_URL", "http://localhost:3000/api")
AUTH_API_ENABLED = os.getenv("AUTH_API_ENABLED", "true").lower() == "true"

auth_service = ProxyAuthService(AUTH_API_URL, AUTH_API_ENABLED)
registry_service = GitHubRegistryService(
    GITHUB_USER, GITHUB_TOKEN, GHCR_REGISTRY)
releases_service = GitHubReleasesService(GITHUB_REPO, GITHUB_TOKEN)
proxy_service = RegistryProxyService(registry_service)


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """Extract and validate Bearer token from Authorization header."""
    return await auth_service.get_current_user(credentials)


@app.get("/v2/")
async def registry_root(request: Request):
    """Docker registry base check."""
    auth_header = request.headers.get("authorization")

    if not auth_header:
        return proxy_service.create_unauthorized_response()

    try:
        if not auth_header.lower().startswith("basic "):
            raise ValueError("Not basic auth")

        token = auth_service.extract_basic_auth_token(auth_header)
        await auth_service.validate_user_token(token)
        return proxy_service.create_success_response()

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Auth failed: {e}")
        return proxy_service.create_unauthorized_response()


@app.api_route("/v2/{path:path}", methods=["GET", "HEAD", "POST", "PUT", "PATCH", "DELETE"])
async def proxy_registry(request: Request, path: str):
    """Proxy to GHCR with OAuth2 token exchange."""
    auth_header = request.headers.get("authorization")

    if not auth_header or not auth_header.lower().startswith("basic "):
        return proxy_service.create_unauthorized_response()

    try:
        token = auth_service.extract_basic_auth_token(auth_header)
        await auth_service.validate_user_token(token)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Auth error: {e}")
        return proxy_service.create_unauthorized_response()

    return await proxy_service.proxy_request(request, path)


@app.get("/firmware/{version}",
         summary="Download firmware",
         description="Download firmware archive from GitHub releases. Use Bearer token for authentication.")
async def get_firmware(version: str, user: dict = Depends(get_current_user)):
    """Download firmware archive from GitHub releases."""
    firmware, filename = await releases_service.get_firmware_archive(version)
    if not firmware:
        raise HTTPException(
            status_code=404, detail="Firmware archive not found")

    return Response(
        content=firmware,
        media_type="application/gzip",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@app.get("/")
async def root():
    return {"status": "ok"}


@app.on_event("shutdown")
async def shutdown_event():
    await auth_service.close()
