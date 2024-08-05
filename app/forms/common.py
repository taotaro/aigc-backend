from typing import Optional
from enum import Enum

from fastapi import Body as _Body
from pydantic import BaseModel as _BaseModel

__all__ = (
    'RegistrationForm',
)



class RegistrationForm(_BaseModel):
    email: str = _Body(..., embed=True)
    name_english: str = _Body(..., embed=True)
    name_chinese: str = _Body(..., embed=True)
    school_name_english: str = _Body(..., embed=True)
    school_name_chinese: str = _Body(..., embed=True)
    school_address_english: str = _Body(..., embed=True)
    school_address_chinese: str = _Body(..., embed=True)
    mobile_phone: str = _Body(..., embed=True)
    telephone: str = _Body(..., embed=True)
    team_name: str = _Body(..., embed=True)
    team_members: list[dict] = _Body(..., embed=True)