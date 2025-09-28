from fastapi import FastAPI, HTTPException
from cryptography import x509
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.backends import default_backend
from datetime import datetime, timedelta
from pydantic import BaseModel

app = FastAPI(
    title="CSR Signer API",
    version="1.0.0",
    description="Microservice for signing Certificate Signing Requests (CSRs) "
                "with the system Certificate Authority (CA)."
)


def load_ca():
    with open("ca/ca.key", "rb") as f:
        key = serialization.load_pem_private_key(f.read(), password=None)
    with open("ca/ca.crt", "rb") as f:
        cert = x509.load_pem_x509_certificate(f.read(), default_backend())
    return key, cert


class CSRRequest(BaseModel):
    """
    Data model for CSR signing requests.

    Attributes
    ----------
    csr_pem : str
        The PEM-encoded Certificate Signing Request (CSR).
    """
    csr_pem: str


@app.post("/sign-csr")
def sign_csr(req: CSRRequest):
    """
    Sign a Certificate Signing Request (CSR) using the CA private key.

    Parameters
    ----------
    req : CSRRequest
        The request body containing a PEM-encoded CSR string.

    Returns
    -------
    dict
        A dictionary with the signed certificate in PEM format.

    Raises
    ------
    HTTPException
        If the CSR signature is invalid (status 400).
    """
    ca_key, ca_cert = load_ca()
    csr = x509.load_pem_x509_csr(
        req.csr_pem.encode(), backend=default_backend())
    if not csr.is_signature_valid:
        raise HTTPException(status_code=400, detail="Invalid CSR signature")

    cert = (
        x509.CertificateBuilder()
        .subject_name(csr.subject)
        .issuer_name(ca_cert.subject)
        .public_key(csr.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.utcnow())
        .not_valid_after(datetime.utcnow() + timedelta(days=365))
        .add_extension(x509.BasicConstraints(ca=False, path_length=None), critical=True)
        .sign(ca_key, hashes.SHA256())
    )
    return {"cert": cert.public_bytes(serialization.Encoding.PEM).decode()}
