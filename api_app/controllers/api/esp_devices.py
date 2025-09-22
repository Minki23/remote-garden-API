from typing import List
from fastapi import APIRouter, Header, Body, Response
from core.dependencies import CurrentUserDep, EspDeviceServiceDep, GardenDep, UserEspAndGardenDep
from models.dtos.esp_device import AssignGardenDTO, EspDeviceDTO
from fastapi import status

router = APIRouter()


@router.post("/register", response_class=Response, status_code=200)
async def register_device(
    service: EspDeviceServiceDep,
    csr_pem: str = Body(..., media_type="application/x-pem-file"),
    x_device_id: str = Header(..., alias="X-Device-ID"),
    x_device_secret: str = Header(..., alias="X-Device-Secret"),
    x_user_key: str = Header(..., alias="X-User-Key"),
):
    cert_pem = await service.process_csr_and_issue_cert(
        device_id=x_device_id, device_secret=x_device_secret, user_key=x_user_key, csr_pem=csr_pem
    )
    return Response(content=cert_pem, media_type="application/x-pem-file")


@router.get("/", response_model=List[EspDeviceDTO], status_code=200)
async def get_esps(
    service: EspDeviceServiceDep,
    user_id: CurrentUserDep
):
    return await service.get_own(user_id)


@router.post("/{esp_id}/assign", status_code=status.HTTP_204_NO_CONTENT)
async def assign_to_garden(
    esp_and_garden: UserEspAndGardenDep,
    service: EspDeviceServiceDep,
):
    await service.assign_to_garden(esp_and_garden[0].id, esp_and_garden[1].id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{esp_id}/unassign", status_code=status.HTTP_204_NO_CONTENT)
async def unassign_from_garden(
    esp_id: int,
    service: EspDeviceServiceDep,
    user_id: CurrentUserDep
):
    await service.unassign_from_garden(esp_id, user_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{esp_id}/reset", status_code=status.HTTP_204_NO_CONTENT)
async def reset_device(
    esp_id: int,
    service: EspDeviceServiceDep,
    user_id: CurrentUserDep
):
    await service.reset_device(esp_id, user_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{esp_id}/resume", status_code=status.HTTP_204_NO_CONTENT)
async def resume_device(
    esp_id: int,
    service: EspDeviceServiceDep,
    user_id: CurrentUserDep
):
    await service.resume_device(esp_id, user_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{esp_id}/stop", status_code=status.HTTP_204_NO_CONTENT)
async def stop_device(
    esp_id: int,
    service: EspDeviceServiceDep,
    user_id: CurrentUserDep
):
    await service.stop_device(esp_id, user_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
