import os
import base64
import httpx
from urllib.parse import unquote
from fastapi import FastAPI, Request, Response, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import logging

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

# Security scheme for Swagger (Bearer token)
security = HTTPBearer()

# Environment
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_USER = os.getenv("GITHUB_USER", "filxxip")
GITHUB_REPO = os.getenv("GITHUB_REPO", "filxxip/remote-garden-ESP")
GHCR_REGISTRY = "https://ghcr.io"
AUTH_API_URL = os.getenv("AUTH_API_URL", "http://localhost:3000/api")
AUTH_API_ENABLED = os.getenv("AUTH_API_ENABLED", "true").lower() == "true"

# Token cache
ghcr_token_cache = {}
auth_client = httpx.AsyncClient(timeout=30.0)


async def validate_user_token(token: str) -> dict:
    """Validate user token via auth API."""
    if not AUTH_API_ENABLED:
        logger.info(">>> Auth disabled, allowing access")
        return {"user_id": "dev-user", "is_admin": True}

    try:
        response = await auth_client.get(
            f"{AUTH_API_URL}/users/me",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
        )

        if response.status_code == 200:
            user_data = response.json()
            if not user_data.get("is_admin", False):
                raise HTTPException(
                    status_code=403, detail="Admin access required")
            return user_data
        elif response.status_code == 401:
            raise HTTPException(
                status_code=401, detail="Invalid or expired token")
        else:
            raise HTTPException(
                status_code=500, detail="Authorization service error")

    except httpx.RequestError as e:
        logger.error(f"Auth service error: {e}")
        if AUTH_API_ENABLED:
            raise HTTPException(
                status_code=503, detail="Auth service unavailable")
        return {"user_id": "fallback-user", "is_admin": True}


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """Extract and validate Bearer token from Authorization header.

    Expects: Authorization: Bearer <token>
    """
    token = credentials.credentials
    return await validate_user_token(token)


async def get_current_user_from_header(request: Request) -> dict:
    """Extract and validate Bearer token from request header (for registry endpoints)."""
    auth_header = request.headers.get("authorization")
    if not auth_header or not auth_header.lower().startswith("basic "):
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        encoded = auth_header.split(" ", 1)[1]
        decoded = base64.b64decode(encoded).decode()
        username, token = decoded.split(":", 1)
    except Exception:
        raise HTTPException(
            status_code=401, detail="Invalid Basic Auth header")

    return await validate_user_token(token)


async def get_ghcr_registry_token(scope: str) -> str:
    """Exchange GitHub PAT for GHCR registry token."""
    if scope in ghcr_token_cache:
        return ghcr_token_cache[scope]

    token_url = "https://ghcr.io/token"
    auth_value = base64.b64encode(
        f"{GITHUB_USER}:{GITHUB_TOKEN}".encode()).decode()

    async with httpx.AsyncClient() as client:
        resp = await client.get(
            token_url,
            params={"scope": scope, "service": "ghcr.io"},
            headers={"Authorization": f"Basic {auth_value}"}
        )

        if resp.status_code == 200:
            token = resp.json().get("token")
            ghcr_token_cache[scope] = token
            logger.info(f">>> Got GHCR token for scope: {scope}")
            return token

        logger.error(f">>> Failed to get GHCR token: {resp.status_code}")
        return None


async def get_firmware_archive(version: str) -> tuple:
    """Download firmware archive from GitHub releases."""
    # Use different endpoint for 'latest'
    if version.lower() == "latest":
        url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
    else:
        url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/tags/{version}"

    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }

    async with httpx.AsyncClient(follow_redirects=True) as client:
        resp = await client.get(url, headers=headers)
        if resp.status_code != 200:
            logger.error(
                f"Failed to get release info: {resp.status_code} - {resp.text}")
            return None, None

        release = resp.json()

        firmware_asset = None
        for asset in release.get("assets", []):
            if asset["name"].endswith((".tar.gz", ".zip", ".bin", ".gz")):
                firmware_asset = asset
                break

        if not firmware_asset:
            logger.error("No firmware asset found in release")
            return None, None

        asset_url = firmware_asset["url"]
        filename = firmware_asset["name"]

        resp = await client.get(
            asset_url,
            headers={
                "Authorization": f"Bearer {GITHUB_TOKEN}",
                "Accept": "application/octet-stream",
                "X-GitHub-Api-Version": "2022-11-28"
            }
        )

        if resp.status_code != 200:
            logger.error(
                f"Failed to download firmware: {resp.status_code} - {resp.text}")
            return None, None

        return resp.content, filename


@app.get("/v2/")
async def registry_root(request: Request):
    """Docker registry base check."""
    auth_header = request.headers.get("authorization")

    if not auth_header:
        return Response(
            status_code=401,
            headers={
                "Docker-Distribution-API-Version": "registry/2.0",
                "WWW-Authenticate": 'Basic realm="Docker Registry"'
            }
        )

    try:
        if not auth_header.lower().startswith("basic "):
            raise ValueError("Not basic auth")

        encoded = auth_header.split(" ", 1)[1]
        decoded = base64.b64decode(encoded).decode()
        username, token = decoded.split(":", 1)

        await validate_user_token(token)

        return Response(
            status_code=200,
            headers={"Docker-Distribution-API-Version": "registry/2.0"}
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Auth failed: {e}")
        return Response(
            status_code=401,
            headers={
                "Docker-Distribution-API-Version": "registry/2.0",
                "WWW-Authenticate": 'Basic realm="Docker Registry"'
            }
        )


@app.api_route("/v2/{path:path}", methods=["GET", "HEAD", "POST", "PUT", "PATCH", "DELETE"])
async def proxy_registry(request: Request, path: str):
    """Proxy to GHCR with OAuth2 token exchange."""
    auth_header = request.headers.get("authorization")

    if not auth_header or not auth_header.lower().startswith("basic "):
        return Response(
            status_code=401,
            headers={
                "Docker-Distribution-API-Version": "registry/2.0",
                "WWW-Authenticate": 'Basic realm="Docker Registry"'
            }
        )

    try:
        encoded = auth_header.split(" ", 1)[1]
        decoded = base64.b64decode(encoded).decode()
        username, token = decoded.split(":", 1)

        await validate_user_token(token)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Auth error: {e}")
        return Response(
            status_code=401,
            headers={
                "Docker-Distribution-API-Version": "registry/2.0",
                "WWW-Authenticate": 'Basic realm="Docker Registry"'
            }
        )

    # Proxy request
    decoded_path = unquote(path)
    target_url = f"{GHCR_REGISTRY}/v2/{decoded_path}"

    # Determine scope for OAuth2 token exchange
    scope = None
    if "/" in decoded_path and ("manifests" in decoded_path or "blobs" in decoded_path):
        parts = decoded_path.split("/")
        if len(parts) >= 2:
            scope = f"repository:{parts[0]}/{parts[1]}:pull"

    headers = dict(request.headers)
    headers.pop("host", None)
    headers.pop("authorization", None)

    # Get GHCR token or use GitHub PAT
    if scope:
        ghcr_token = await get_ghcr_registry_token(scope)
        if ghcr_token:
            headers["Authorization"] = f"Bearer {ghcr_token}"
        else:
            return Response(status_code=500, content=b"Failed to authenticate with GHCR")
    else:
        auth_value = base64.b64encode(
            f"{GITHUB_USER}:{GITHUB_TOKEN}".encode()).decode()
        headers["Authorization"] = f"Basic {auth_value}"

    body = await request.body() if request.method not in ["GET", "HEAD"] else None

    async with httpx.AsyncClient() as client:
        resp = await client.request(
            method=request.method,
            url=target_url,
            headers=headers,
            params=request.query_params,
            content=body,
            timeout=60.0,
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


@app.get("/firmware/{version}",
         summary="Download firmware",
         description="Download firmware archive from GitHub releases. Use Bearer token for authentication.")
async def get_firmware(version: str, user: dict = Depends(get_current_user)):
    """Download firmware archive from GitHub releases.

    Authentication: Use Bearer token in Authorization header.
    """
    firmware, filename = await get_firmware_archive(version)
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
    await auth_client.aclose()
