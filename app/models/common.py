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
)

class GenderEnum(Enum):
    male = 'male'
    female = 'female'


class TeacherModel(BaseDBModel):
    # special string type that validates the email as a string
    email: Annotated[str, Indexed(EmailStr, unique=True)] = Field(...)
    name_english: str = Field(...)
    name_chinese: str = Field(...)
    school_name_chinese: str = Field(...)
    school_name_english: str = Field(...)
    school_address_chinese: str = Field(...)
    school_address_english: str = Field(...)
    mobile_phone: Optional[str] = Field(None)
    telephone: Optional[str] = Field(None)

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
            'schoolAddressChinese': self.school_address_chinese,
            'schoolAddressEnglish': self.school_address_english,
            'mobilePhone': self.mobile_phone,
            'telephone': self.telephone,
        }

class StudentModel(BaseDBModel):
    name_english: str = Field(...)
    name_chinese: str = Field(...)
    year_of_birth: int = Field(...)
    gender: GenderEnum = Field(...)
    grade: int = Field(...)
    teacher_email: Annotated[str, Indexed(EmailStr)] = Field(...)

    class Settings:
        name = 'students'
        strict = False
        indexes = [
            [('_id', HASHED)],
        ]

class TeamModel(BaseDBModel):
    name: str = Field(...)
    members: List[StudentModel] = Field(...)
    teacher_email: Annotated[str, Indexed(EmailStr)] = Field(...)

    class Settings:
        name = 'teams'
        strict = False
        indexes = [
            [('_id', HASHED)],
        ]
    