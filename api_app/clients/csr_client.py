import httpx
from exceptions.scheme import AppException


class CsrClient:
    def __init__(self, base_url: str = "http://csr-signer:8000"):
        self.base_url = base_url.rstrip("/")

    async def sign_csr(self, csr_pem: str) -> str:
        payload = {"csr_pem": csr_pem}

        async with httpx.AsyncClient() as client:
            resp = await client.post(f"{self.base_url}/sign-csr", json=payload)

        if resp.status_code != 200:
            raise AppException(f"CA service error: {resp.text}")

        data = resp.json()
        if "cert" not in data:
            raise AppException("Invalid response from CA service")

        return data["cert"]
