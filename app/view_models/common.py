import bcrypt
from fastapi import Request
from httpx import ReadTimeout
from httpx import TimeoutException

from app.config import get_settings
from app.forms.common import *
from app.models import *
from app.view_models import BaseViewModel
from app.models.common import *

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
        print('register')
        teacher = await TeacherModel.find_one(TeacherModel.email == self.form_data.email)
        if teacher:
            self.forbidden('email already registered for another team')
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
        ).insert()
        team_member_info = []
        for team in self.form_data.team_members:
            student_info = await StudentModel(
                name_english=team['name_english'],
                name_chinese=team['name_chinese'],
                year_of_birth=team['year_of_birth'],
                gender=team['gender'],
                grade=team['grade'],
                teacher_email=self.form_data.email
            ).insert()
            team_member_info.append(student_info)

        team_info = await TeamModel(
            name=self.form_data.team_name,
            members=team_member_info,
            teacher_email=self.form_data.email
        ).insert()

        email_body = f"""
            Dear Team,

            You have successfully registered a team under {self.form_data.email}
            with the name {self.form_data.team_name}.

            The members of the team are as follows:
            """
    
        for idx, member in enumerate(self.form_data.team_members, start=1):
            email_body += f"""
                {idx}. Name (in Chinese): {member['name_chinese']}
                Name (in English): {member['name_english']}
                Year of Birth: {member['year_of_birth']}
                Gender: {member['gender']}
                Grade: {member['grade']}
                """


        self.send_email(
            get_settings().MAIL_USERNAME,
            self.form_data.email,
            email_body,
            'Registration of team successful'
        )

        self.operating_successfully(dict(teacher_info) | dict(team_info))

    