from pydantic import BaseModel


class SignupModel(BaseModel):
    name: str
    email: str
    password: str


class LoginModel(BaseModel):
    email: str
    password: str


class RefreshModel(BaseModel):
    refresh_token: str