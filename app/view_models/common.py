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

__all__ = (
    'RegistrationViewModel',
)


class RegistrationViewModel(BaseViewModel):

    def __init__(self, form_data: RegistrationForm):
        super().__init__(need_auth=False)
        self.form_data = form_data

    async def before(self):
        try:
            await self.register()
        except TimeoutException as e:
            self.request_timeout(str(e))

    async def register(self):
        # print('register')
        print('data: ', self.form_data)
        teacher = await TeacherModel.find_one(TeacherModel.email == self.form_data.email)
        if teacher:
            self.forbidden('email already registered for another team')
        
        all_team_info = []
        team_member_info = []
        for team in self.form_data.team_info:
            for member in team['team_members']:
                student_info = await StudentModel(
                    name_english=member['name_english'],
                    name_chinese=member['name_chinese'],
                    year_of_birth=member['year_of_birth'],
                    gender=member['gender'],
                    grade=member['grade'],
                    teacher_email=self.form_data.email
                ).insert()
                team_member_info.append(student_info)

            team_info = await TeamModel(
                name=team['team_name'],
                members=team_member_info,
                teacher_email=self.form_data.email
            ).insert()
            all_team_info.append({
                'team_name': team['team_name'],
                'members': team_member_info,
            })


        teacher_info = await TeacherModel(
            email=self.form_data.email,
            name_english=self.form_data.name_english,
            name_chinese=self.form_data.name_chinese,
            school_name_english=self.form_data.school_name_english,
            school_name_chinese=self.form_data.school_name_chinese,
            school_address_english=self.form_data.school_address_english,
            school_address_chinese=self.form_data.school_address_chinese,
            mobile_phone=self.form_data.mobile_phone,
            telephone=self.form_data.telephone,
            title=self.form_data.title,
            teams=all_team_info
        ).insert()

        email_body = render_template('registration_email.html', {
            # 'team_name': self.form_data.team_name,
            'email': self.form_data.email,
            'info': self.form_data.team_info
        })

        self.send_email(
            get_settings().MAIL_USERNAME,
            self.form_data.email,
            email_body,
            'Registration of team successful'
        )

        self.operating_successfully(dict(teacher_info) | dict(team_info))

    