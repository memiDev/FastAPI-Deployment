from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserBase(BaseModel):
    username: str = Field(min_length=1, max_length=50)
    email: EmailStr = Field(max_length=120)


class UserCreate(UserBase):
    password: str = Field(min_length=8)


class UserPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    image_file: str | None
    image_path: str # The logic to create this, is in models.User.image_path


class UserPrivate(UserPublic):
    email: EmailStr


class UserUpdate(BaseModel):
    username: str | None = Field(default=None, min_length=1, max_length=50)
    email: EmailStr | None = Field(default=None, max_length=120)


class Token(BaseModel):
    access_token: str
    token_type: str


class PostBase(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    content: str = Field(min_length=1)


class PostCreate(PostBase):
    # Defines what we get when post is created which will give more flexibility later
    pass

class PostUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=100)
    content: str | None = Field(default=None, min_length=1)


class PostResponse(PostBase):
    # Defines what we return in the API
    # Allows to read data objects (like ORMS) with attributes and not just dicts
    model_config = ConfigDict(from_attributes=True)

    # Fields that the client does not provide
    id: int
    user_id: int
    date_posted: datetime
    author: UserPublic


class PaginatedPostsResponse(BaseModel):
    # skip = 20, limit = 10 gives the post from 21 to 30
    posts: list[PostResponse]
    total: int  # total count of posts in the db
    skip: int # current offset
    limit: int # how many posts requested
    has_more: bool # enables the frontend to show that there are more posts to load without loading them unless the client wants


class ForgotPasswordRequest(BaseModel):
    email: EmailStr = Field(max_length=120)


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(min_length=8)


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(min_length=8)

