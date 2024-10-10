import bcrypt
from fastapi import Request
from httpx import ReadTimeout
from httpx import TimeoutException, ReadTimeout

from app.config import get_settings
from app.forms.common import *
from app.models import *
from app.view_models import BaseViewModel
from app.models.common import *
from app.libs.custom import render_template
import pandas as pd
from io import BytesIO
import secrets
from motor.motor_asyncio import AsyncIOMotorClient
import msoffcrypto
from fastapi.responses import StreamingResponse
from datetime import datetime
import re

__all__ = (
    'RegistrationViewModel',
    'AllDataViewModel',
    'LoginViewModel',
    'RegisterEmailViewModel',
    'BatchSendEmailModel',
    'BatchSendWorkshopEmailModel',
    'AddDataToDatabaseViewModel',
)


class RegistrationViewModel(BaseViewModel):

    def __init__(self, form_data: RegistrationForm):
        super().__init__(need_auth=False)
        self.form_data = form_data

    async def before(self):
        if '@' not in self.form_data.email:
            self.operating_failed('電子郵件地址無效')
        try:
            await self.register()
        except TimeoutException as e:
            self.request_timeout(str(e))

    async def register(self):
        print('registering...: ', self.form_data)
        all_team_info = []
        
        for team in self.form_data.team_info:
            team_member_info = []
            for member in team['team_members']:
                student_info = await StudentModel(
                    name_chinese=member['name_chinese'],
                    grade=member['grade'],
                    teacher_email=self.form_data.email
                ).insert()
                team_member_info.append(student_info)

            secret_code = str(secrets.randbelow(10**12)).zfill(12)

            team_info = await TeamModel(
                name=team['team_name'],
                members=team_member_info,
                school_group=team['school_group'],
                teacher_email=self.form_data.email,
                secret_code=secret_code
            ).insert()
            all_team_info.append({
                'team_name': team['team_name'],
                'school_group': team['school_group'],
                'members': team_member_info,
                'secret_code': secret_code
            })


        teacher_info = await TeacherModel(
            email=self.form_data.email,
            name_english=self.form_data.name_english,
            name_chinese=self.form_data.name_chinese,
            school_name_english=self.form_data.school_name_english,
            school_name_chinese=self.form_data.school_name_chinese,
            mobile_phone=self.form_data.mobile_phone,
            telephone=self.form_data.telephone,
            title=self.form_data.title,
            teams=all_team_info
        ).insert()

        email_body = render_template('registration_email.html', {
            'email': self.form_data.email,
            'teacher_name_chinese': self.form_data.name_chinese,
            'teacher_name_english': self.form_data.name_english,
            'school_name_chinese': self.form_data.school_name_chinese,
            'school_name_english': self.form_data.school_name_english,
            'mobile_phone': self.form_data.mobile_phone,
            'telephone': self.form_data.telephone,
            # 'info': self.form_data.team_info,
            'info': all_team_info
        })

        email_status = self.send_email(
            get_settings().MAIL_USERNAME,
            self.form_data.email,
            email_body,
            '雲遊通義 – 阿里雲香港AI比賽報名完成'
        )
        print('email sent: ', email_status)

        self.operating_successfully(dict(teacher_info) | dict(team_info))


class AllDataViewModel(BaseViewModel):

    def __init__(self, request: Request):
        super().__init__(request=request)
        print('self.token: ', self.token)

    
    async def before(self):
        try:
            await self.get_all_data()
        except ReadTimeout as e:
            self.request_timeout(str(e))

    async def get_all_data(self):
        
        data_list = await TeacherModel.find_all().to_list()

        all_records = []
        for data in data_list:
            for team in data['teams']:
                if 'secret_code' in team:
                    secret_code = team['secret_code']
                else:
                    secret_code = None
                print('data: ', data.createdAt)
                created_at = data.createdAt
                print('created_at: ', created_at)
                formatted_created_at = datetime.strptime(str(created_at), "%Y-%m-%d %H:%M:%S.%f")
                for index, member in enumerate(team['members']):
                    all_records.append({
                        "Created At": formatted_created_at.strftime("%Y-%m-%d %H:%M:%S"),
                        "School Name": data["school_name_english"],
                        "School Name CN": data["school_name_chinese"],
                        "Teacher Name": data["name_english"],
                        "Teacher Name CN": data["name_chinese"],
                        "School Phone": data["mobile_phone"],
                        "Telephone": data["telephone"],
                        "Email": data["email"],
                        "Team Number": team["team_name"],
                        "School Group": team["school_group"],
                        'Secret Code': secret_code,
                        "Member Position": "Leader" if index == 0 else None,
                        "Student Name": member["name_chinese"],
                        "Grade": member["grade"],
                    })

        df = pd.DataFrame(all_records)
        self.excel_file = BytesIO()
        df.to_excel(self.excel_file, index=False, engine='openpyxl')
        
        self.excel_file.seek(0)

        password = get_settings().FILE_PASSWORD  # Set your password here

        # Create a new buffer to hold the encrypted file
        encrypted_file = BytesIO()

        # Load the unencrypted Excel file into msoffcrypto
        excel_file = msoffcrypto.OfficeFile(self.excel_file)
        excel_file.load_key(password=password)  # Set the password

        # Encrypt the file and write the encrypted content to the new buffer
        excel_file.encrypt(outfile=encrypted_file, password=password)

        # Reset the pointer to the start of the encrypted file
        encrypted_file.seek(0)

        # Replace the original file buffer with the encrypted one
        self.excel_file = encrypted_file
        self.operating_successfully(self.excel_file)


class RegisterEmailViewModel(BaseViewModel):

    def __init__(self, form_data: RegisterPassword):
        super().__init__(need_auth=False)

        self.form_data = form_data

    async def before(self):
        try:
            await self.register()
        except TimeoutException as e:
            self.request_timeout(str(e))

    async def register(self):
        # email = self.form_data.email.lower()
        # user = await LoginModel.find_one(LoginModel.email == email)
        # if user:
        #     self.forbidden('email already exists')
        salt = bcrypt.gensalt()
        password = bcrypt.hashpw(self.form_data.password.encode('utf-8'), salt)
        # user_info = await LoginModel(email=email, password=password).insert()
        user_info = await LoginModel(password=password, role='admin').insert()
        token = self.create_token()

        self.operating_successfully(dict(user_info) | {'token': token})




class LoginViewModel(BaseViewModel):

    def __init__(self, form_data: LoginForm):
        super().__init__(need_auth=False)

        self.form_data = form_data

    async def before(self):
        try:
            await self.login()
        except TimeoutException as e:
            self.request_timeout(str(e))

    async def login(self):
        user = await LoginModel.find_one(LoginModel.role=='admin')
       
        if not bcrypt.checkpw(self.form_data.password.encode('utf-8'), user.password.encode('utf-8')):
            self.operating_failed('invalid password')
        token = self.create_token()

        self.operating_successfully(
            {
                'message': 'login successfully',
                'token': token
            } 
        )

class BatchSendEmailModel(BaseViewModel):
    def __init__(self, email):
        super().__init__(need_auth=False)
        self.email = email

    async def before(self):
        try:
            await self.batch_send()
        except TimeoutException as e:
            self.request_timeout(str(e))

    async def batch_send(self):
        # all_data = await TeacherModel.find_all().to_list()
        all_data = await TeacherModel.find(TeacherModel.email==self.email).to_list()
        for item in all_data:
            # print(item.email)
            email_body = render_template('registration_email.html', {
            'email': item.email,
            'teacher_name_chinese': item.name_chinese,
            'teacher_name_english': item.name_english,
            'school_name_chinese': item.school_name_chinese,
            'school_name_english': item.school_name_english,
            'mobile_phone': item.mobile_phone,
            'telephone': item.telephone,
            # 'info': self.form_data.team_info,
            'info': item.teams
        })
            email_status = self.send_email(
                get_settings().MAIL_USERNAME,
                item.email,
                # 'kgb@materia-logic.com',
                email_body,
                '雲遊通義 – 阿里雲香港AI比賽報名完成'
            )
            print('email sent: ', item.email, email_status)

        self.operating_successfully('batch emails sent')


class BatchSendWorkshopEmailModel(BaseViewModel):
    def __init__(self, csv_data):
        super().__init__(need_auth=False)
        self.csv_data = csv_data

    async def before(self):
        try:
            await self.batch_send()
        except TimeoutException as e:
            self.request_timeout(str(e))

    async def batch_send(self):
        # print(self.csv_data)
        for item in self.csv_data.values:
            print(item)
            school_name = item[0]
            created_at = item[1]
            submitter = item[2]
            name = item[3]
            email = item[4]
            number = item[5]
            participants_9th = item[6]
            pariticipants_14th = item[7]

            email_body = render_template('workshop_email.html', {
                'school_name': school_name,
                'teacher_name': name,
                'teacher_email': email,
                'teacher_mobile': number,
                'participants_1': participants_9th,
                'participants_2': pariticipants_14th
            })
            email_status = self.send_email(
                get_settings().MAIL_USERNAME,
                'kgb@materia-logic.com',
                # email,
                email_body,
                '雲遊通義 – 阿里雲香港AI比賽線上工作坊報名完成'
            )
        # email_status = self.send_email(
        #         get_settings().MAIL_USERNAME,
        #         'kgb@materia-logic.com',
        #         email_body,
        #         '雲遊通義 – 阿里雲香港AI比賽報名完成'
        # )



class AddDataToDatabaseViewModel(BaseViewModel):
    def __init__(self):
        super().__init__(need_auth=False)

    async def before(self):
        try:
            await self.format_data_for_insertion()
        except TimeoutException as e:
            self.request_timeout(str(e))

    def extract_team_number(self, team):
            return int(re.search(r'\d+', team).group())

    async def format_data_for_insertion(self):
    # Load the Excel file into a DataFrame
        data = pd.read_excel('data.xlsx')

        

    # Group the data by team and teacher for easier manipulation
        grouped_data = data.groupby(['Email', 'Team Number']).apply(lambda x: {
        'team_name': x['Team Number'].iloc[0],
        'school_group': x['School Group'].iloc[0],
        'team_members': [{
            'name_chinese': row['Student Name'],
            'grade': row['Grade'],
        } for _, row in x.iterrows()],
        }).reset_index()

        grouped_data['team_name_numeric'] = grouped_data['Team Number'].apply(self.extract_team_number)
        grouped_data = grouped_data.sort_values('team_name_numeric')

    # Structure data for each teacher
        teacher_data = data.groupby('Email').apply(lambda x: {
        'email': x['Email'].iloc[0],
        'name_english': x['Teacher Name'].iloc[0],
        'name_chinese': x['Teacher Name CN'].iloc[0],
        'school_name_english': x['School Name'].iloc[0],
        'school_name_chinese': x['School Name CN'].iloc[0],
        'mobile_phone': x['Telephone'].iloc[0],
        'telephone': x['School Phone'].iloc[0],
        'teams': grouped_data[grouped_data['Email'] == x['Email'].iloc[0]][0].tolist()
        }).tolist()

        # return teacher_data
        print(teacher_data)
        for teacher in teacher_data:
            all_team_info = []
            for team in teacher['teams']:
                team_member_info = []
                for member in team['team_members']:
                    student_info = await StudentModel(
                        name_chinese=member['name_chinese'],
                        grade=member['grade'],
                    teacher_email=teacher['email']
                    ).insert()
                    team_member_info.append(student_info)
                secret_code = str(secrets.randbelow(10**12)).zfill(12)

                team_info = await TeamModel(
                    name=team['team_name'],
                    members=team_member_info,
                    school_group=team['school_group'],
                    teacher_email=teacher['email'],
                    secret_code=secret_code
                ).insert()
            
            
                all_team_info.append({
                    'team_name': team['team_name'],
                    'school_group': team['school_group'],
                    'members': team_member_info,
                    'secret_code': secret_code
                })

            teacher_info = await TeacherModel(
                email=teacher['email'],
                name_english=teacher['name_english'],
                name_chinese=teacher['name_chinese'],
                school_name_english=teacher['school_name_english'],
                school_name_chinese=teacher['school_name_chinese'],
                mobile_phone=str(teacher['mobile_phone']),
                telephone=str(teacher['telephone']),
                title='Ms.',  # Assuming title is hardcoded, update if necessary
                teams=all_team_info
            ).insert()

            email_body = render_template('registration_email.html', {
            'email': teacher['email'],
            'teacher_name_chinese':teacher['name_english'] ,
            'teacher_name_english':teacher['name_chinese'],
            'school_name_english': teacher['school_name_english'],
            'school_name_chinese': teacher['school_name_chinese'],
            'mobile_phone': teacher['mobile_phone'],
            'telephone': teacher['telephone'],
            # 'info': self.form_data.team_info,
            'info': all_team_info
            })

            email_status = self.send_email(
            get_settings().MAIL_USERNAME,
            # 'kgb@materia-logic.com',
            teacher['email'],
            email_body,
            '雲遊通義 – 阿里雲香港AI比賽報名完成'
            )
            print('email sent: ', email_status)
       
