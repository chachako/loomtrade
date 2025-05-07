from typing import Optional

from pydantic import BaseModel, EmailStr


# Shared properties
class UserBase(BaseModel):
  """
  用户模型的基础 Pydantic schema，包含通用属性。
  """
  email: Optional[EmailStr] = None
  is_active: Optional[bool] = True
  is_superuser: bool = False
  full_name: Optional[str] = None


# Properties to receive via API on creation
class UserCreate(UserBase):
  """
  用于创建新用户的 Pydantic schema。
  需要 email 和密码。
  """
  email: EmailStr
  username: str
  password: str


# Properties to receive via API on update
class UserUpdate(UserBase):
  """
  用于更新现有用户的 Pydantic schema。
  所有字段都是可选的。
  """
  password: Optional[str] = None


# Properties shared by models stored in DB
class UserInDBBase(UserBase):
  """
  存储在数据库中的用户模型的基础 Pydantic schema。
  包含 id 属性。
  """
  id: Optional[int] = None

  class Config:
    orm_mode = True # 在 Pydantic V2 中是 from_attributes = True


# Additional properties stored in DB but not returned by API
class UserInDB(UserInDBBase):
  """
  表示数据库中完整用户记录的 Pydantic schema。
  包含哈希密码。
  """
  hashed_password: str


# Additional properties to return via API
class User(UserInDBBase):
  """
  通过 API 返回给客户端的用户 Pydantic schema。
  不包含敏感信息如 hashed_password。
  """
  pass