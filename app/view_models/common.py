import bcrypt
from fastapi import Request
from httpx import ReadTimeout
from httpx import TimeoutException

from app.config import get_settings
from app.forms.common import *
from app.models import *
from app.view_models import BaseViewModel
from app.models.common import *
from app.libs.custom import render_template
import pandas as pd
from io import BytesIO
import secrets

__all__ = (
    'RegistrationViewModel',
    'AllDataViewModel',
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

    def __init__(self):
        super().__init__(need_auth=False)

    async def before(self):
        try:
            await self.get_all_data()
        except TimeoutException as e:
            self.request_timeout(str(e))

    async def get_all_data(self):
        data_list = await TeacherModel.find_all().to_list()

        all_records = []
        for data in data_list:
            for team in data['teams']:
                print(team)
                if 'secret_code' in team:
                    secret_code = team['secret_code']
                else:
                    secret_code = None
                for index, member in enumerate(team['members']):
                    all_records.append({
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


    