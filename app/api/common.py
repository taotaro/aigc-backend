from fastapi import APIRouter, Request, File, UploadFile, Query
import pandas as pd
from io import StringIO
from fastapi.responses import StreamingResponse

from app.forms.common import *
from app.view_models.common import *
from app.libs.constants import ResponseStatusCodeEnum, get_response_message

router = APIRouter(
    prefix='/common', tags=['Common API'], dependencies=[]
)

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


@router.post('/batch-send-email')
async def batch_send(email: str = Query(..., description="email address")):
    async with BatchSendEmailModel() as response:
        return response

@router.post('/batch-send-email-workshop')
async def batch_send(
    file: UploadFile = File(...), 
    from_row: int = Query(..., description="Starting row number (inclusive)"),
    to_row: int = Query(..., description="Ending row number (inclusive)")):
    content = await file.read()
    csv_data = pd.read_csv(StringIO(content.decode('utf-8')))
    filtered_data = csv_data.iloc[from_row-2:to_row-1]
    # print('csv_data: ', csv_data)
    async with BatchSendWorkshopEmailModel(filtered_data) as response:
        return response

@router.post('/add-data')
async def add_data():
    async with AddDataToDatabaseViewModel() as response:
        return response



    