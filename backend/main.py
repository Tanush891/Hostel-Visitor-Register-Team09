from datetime import date
from pathlib import Path

from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, EmailStr, Field, field_validator

import functions

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class RegisterIn(BaseModel):
    username: str = Field(min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)

    @field_validator("username")
    @classmethod
    def username_cannot_be_blank(cls, value):
        value = value.strip()
        if value == "":
            raise ValueError("Username cannot be empty")
        return value


class LoginIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=72)


class RefreshIn(BaseModel):
    refresh_token: str = Field(min_length=1)


class VisitorIn(BaseModel):
    visitor_name: str = Field(min_length=1, max_length=160)
    student_name: str = Field(min_length=1, max_length=160)
    room_no: str = Field(min_length=1, max_length=30)
    purpose: str = Field(min_length=1, max_length=500)
    visit_date: date

    @field_validator("visitor_name", "student_name", "room_no", "purpose")
    @classmethod
    def text_cannot_be_blank(cls, value):
        value = value.strip()
        if value == "":
            raise ValueError("This field cannot be empty")
        return value


@app.post("/auth/register", status_code=201)
def register_staff(user: RegisterIn):
    result = functions.add_user(
        username=user.username,
        email=user.email,
        password=user.password,
    )
    if not result:
        raise HTTPException(status_code=409, detail="Email already registered")
    return {"message": "Staff registered successfully"}


@app.post("/auth/login")
def login(user: LoginIn):
    token = functions.verify_login(email=user.email, password=user.password)
    if not token:
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    return token