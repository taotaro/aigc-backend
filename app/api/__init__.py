from typing import Annotated

from fastapi import APIRouter, Depends

from app.config import Settings, get_settings
# from app.models.payment.manual_pay import PaymentNetworkModel

router = APIRouter(
    prefix='', tags=['Root API'], dependencies=[]
)


@router.get("/")
async def test_api():
    return 'API is working'
