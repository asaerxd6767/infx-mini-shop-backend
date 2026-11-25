from pydantic import BaseModel, ConfigDict, Field, EmailStr

class NewUser(BaseModel):
    name: str
    email: EmailStr
    password: str = Field(min_length=8)


class UserRead(BaseModel):
    id: int
    name: str
    email: str

    model_config = ConfigDict(from_attributes=True)
