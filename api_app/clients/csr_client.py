import httpx
from core.config import CONFIG
from exceptions.scheme import AppException


class CsrClient:
    """
    Client for interacting with the Certificate Authority (CA) service.
    """

    async def sign_csr(self, csr_pem: str) -> str:
        """
        Submit a Certificate Signing Request (CSR) to the CA service.

        Parameters
        ----------
        csr_pem : str
            The CSR in PEM format that should be signed by the CA.

        Returns
        -------
        str
            The signed certificate in PEM format.

        Raises
        ------
        AppException
            If the CA service responds with a non-200 status code,
            or if the response does not contain a valid certificate.
        """
        payload = {"csr_pem": csr_pem}

        async with httpx.AsyncClient() as client:
            resp = await client.post(f"{CONFIG.BASE_CSR_URL}/sign-csr", json=payload)

        if resp.status_code != 200:
            raise AppException(f"CA service error: {resp.text}")

        data = resp.json()
        if "cert" not in data:
            raise AppException("Invalid response from CA service")

        return data["cert"]
