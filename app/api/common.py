from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse

from app.forms.common import *
from app.view_models.common import *

router = APIRouter(
    prefix='/common', tags=['Common API'], dependencies=[]
)

@router.post('/register')
async def register_account(form_data: RegistrationForm):
    async with RegistrationViewModel(form_data) as response:
        return response

@router.get("/wRhfMDBJY0FrbZzEdiE1fKtZ5HXPGVo0")
async def excel_data_export():
    async with AllDataViewModel() as response:
        if response.excel_file:
            return StreamingResponse(response.excel_file, media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', headers={'Content-Disposition': 'attachment; filename=Registration_Data.xlsx'})
        else:
            return 'No data found'


@router.post('/log-error')
async def log_error(form_data: LogErrorForm):
    print('logging error: ', form_data)
    return {'status':'error logged'}





    