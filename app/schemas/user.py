from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class UserCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str = Field(min_length=2, max_length=50)
    email: EmailStr
    age: int = Field(ge=18, le=120)
    is_active: bool = True


class UserResponse(UserCreate):
    id: int


class UserUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str | None = Field(default=None, min_length=2, max_length=50)
    email: EmailStr | None = None
    age: int | None = Field(default=None, ge=18, le=120)
    is_active: bool | None = None

    @field_validator("name", "email", "age", "is_active")
    @classmethod
    def reject_null(cls, value: object) -> object:
        if value is None:
            raise ValueError("Field cannot be null")
        return value
