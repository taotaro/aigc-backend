from datetime import datetime
from enum import IntEnum, Enum
from typing import List, Annotated, Optional

from beanie import Indexed
from pydantic import Field, EmailStr, BaseModel
from pymongo import IndexModel, HASHED, TEXT

from app.models import BaseDBModel

__all__ = (
    'TeacherModel',
    'TeamModel',
    'GenderEnum',
    'StudentModel',
    'TitleEnum',
    'LoginModel',
)

class GenderEnum(Enum):
    男性 = '男性'
    女性 = '女性'

class TitleEnum(Enum):
    Mr = 'Mr.'
    Mrs = 'Mrs.'
    Miss = 'Miss.'
    Dr = 'Dr.'
    Prof = 'Prof.'
    Ms = 'Ms.'

class SchoolGroupEnum(Enum):
    小學組= '小學組'
    中學組 = '中學組'
    展能組 = '展能組'

class TeacherModel(BaseDBModel):
    # special string type that validates the email as a string
    email: Annotated[str, Indexed(EmailStr)] = Field(...)
    name_english: str = Field(...)
    name_chinese: str = Field(...)
    title: TitleEnum = Field(...)
    school_name_chinese: str = Field(...)
    school_name_english: str = Field(...)
    # school_address_chinese: str = Field(...)
    # school_address_english: str = Field(...)
    mobile_phone: str = Field(...)
    telephone: str = Field(...)
    teams: List[dict] = Field([])
    

    class Settings:
        name = 'teachers'
        strict = False
        indexes = [
            [('_id', HASHED)],
        ]

    @property
    def information(self):
        return {
            'email': self.email,
            'nameChinese': self.name_chinese,
            'nameEnglish': self.name_english,
            'schoolNameChinese': self.school_name_chinese,
            'schoolNameEnglish': self.school_name_english,
            # 'schoolAddressChinese': self.school_address_chinese,
            # 'schoolAddressEnglish': self.school_address_english,
            'mobilePhone': self.mobile_phone,
            'telephone': self.telephone,
        }

class StudentModel(BaseDBModel):
    # name_english: str = Field(...)
    name_chinese: str = Field(...)
    # year_of_birth: int = Field(...)
    # gender: GenderEnum = Field(...)
    grade: str = Field(...)
    # school_group: SchoolGroupEnum = Field(...)
    # mobile_phone: Optional[str] = Field(None)
    # email: Optional[str] = Field(None)
    teacher_email: Annotated[str, Indexed(EmailStr)] = Field(...)

    class Settings:
        name = 'students'
        strict = False
        indexes = [
            [('_id', HASHED)],
        ]

class TeamModel(BaseDBModel):
    name: str = Field(...)
    school_group: SchoolGroupEnum = Field(...)
    members: List[StudentModel] = Field(...)
    teacher_email: Annotated[str, Indexed(EmailStr)] = Field(...)
    secret_code: Optional[str] = Field(None)

    class Settings:
        name = 'teams'
        strict = False
        indexes = [
            [('_id', HASHED)],
        ]
    

class LoginModel(BaseDBModel):
    role: str = Field(...)
    password: str = Field(...)

    class Settings:
        name = 'login'
        strict = False
        indexes = [
            [('_id', HASHED)],
        ]