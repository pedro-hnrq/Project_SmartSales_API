from typing import List, Optional

from pydantic import BaseModel, EmailStr, field_validator

from smartsales.utils.validators import validate_cpf, validate_full_name


class ClientBase(BaseModel):
    name: str
    email: EmailStr
    cpf: str

    @field_validator('cpf')
    def validate_cpf(cls, v):
        return validate_cpf(v)

    @field_validator('name')
    def validate_name(cls, v):
        return validate_full_name(v)


class ClientCreate(ClientBase):
    pass


class ClientUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    cpf: Optional[str] = None


class OwnerSchema(BaseModel):
    email: EmailStr
    role: str

    class Config:
        from_attributes = True


class ClientResponse(ClientBase):
    id: int
    owner: OwnerSchema

    class Config:
        from_attributes = True


class ClientListResponse(BaseModel):
    total: int
    items: List[ClientResponse]
