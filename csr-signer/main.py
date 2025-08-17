from fastapi import FastAPI, HTTPException
from cryptography import x509
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.backends import default_backend
from datetime import datetime, timedelta

app = FastAPI()

with open("ca/ca.key", "rb") as f:
    ca_key = serialization.load_pem_private_key(f.read(), password=None)

with open("ca/ca.crt", "rb") as f:
    ca_cert = x509.load_pem_x509_certificate(f.read(), default_backend())


@app.post("/sign-csr")
def sign_csr(csr_pem: str):
    csr = x509.load_pem_x509_csr(csr_pem.encode(), backend=default_backend())
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
