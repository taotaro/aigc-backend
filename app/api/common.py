from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse

from app.forms.common import *
from app.view_models.common import *
from app.libs.constants import ResponseStatusCodeEnum, get_response_message

router = APIRouter(
    prefix='/common', tags=['Common API'], dependencies=[]
)

@router.get("/")
async def test_api():
    return 'API is working'
    
@router.post('/register')
async def register_account(form_data: RegistrationForm):
    async with RegistrationViewModel(form_data) as response:
        return response

@router.get("/excel")
async def excel_data_export(request: Request):
    async with AllDataViewModel(request=request) as response:
        if response.code == ResponseStatusCodeEnum.OPERATING_SUCCESSFULLY.value:
            print('response.data: ', response.data)
            return StreamingResponse(response.data, media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', headers={'Content-Disposition': 'attachment; filename=Registration_Data.xlsx'})
        return response
        # if response.excel_file:
        #     return StreamingResponse(response.excel_file, media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', headers={'Content-Disposition': 'attachment; filename=Registration_Data.xlsx'})
        # else:
        #     return 'No data found'


@router.post('/log-error')
async def log_error(form_data: LogErrorForm):
    print('logging error: ', form_data)
    return {'status':'error logged'}


@router.post('/register-password')
async def register_email(form_data: RegisterPassword):
    async with RegisterEmailViewModel(form_data) as response:
        return response


@router.post('/login')
async def login(form_data: LoginForm):
    async with LoginViewModel(form_data) as response:
        return response





    