from fastapi import APIRouter, Request

from app.forms.common import *
from app.view_models.common import *

router = APIRouter(
    prefix='/common', tags=['Common API'], dependencies=[]
)


@router.post('/register')
async def register_account(form_data: RegistrationForm):
    async with RegistrationViewModel(form_data) as response:
        return response