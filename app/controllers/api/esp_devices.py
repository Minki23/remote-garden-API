from fastapi import APIRouter, Header, Body, Response
from app.core.dependencies import EspDeviceServiceDep

router = APIRouter()


@router.post("/register", response_class=Response, status_code=200)
async def register_device(
    service: EspDeviceServiceDep,
    csr_pem: str = Body(..., media_type="application/x-pem-file"),
    x_device_id: str = Header(..., alias="X-Device-ID"),
    x_device_secret: str = Header(..., alias="X-Device-Secret"),
):
    cert_pem = await service.process_csr_and_issue_cert(
        device_id=x_device_id, device_secret=x_device_secret, csr_pem=csr_pem
    )
    return Response(content=cert_pem, media_type="application/x-pem-file")
