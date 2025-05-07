from typing import Any, Dict, Optional, Union

from sqlalchemy.orm import Session

from app.core.security import get_password_hash
# Removed verify_password import as it's not directly used in CRUD, but in auth logic
from app.models.user import Users as UserModel
from app.schemas.user import UserCreate, UserUpdate


def get_user(db: Session, user_id: int) -> Optional[UserModel]:
  """
  通过用户 ID 从数据库中获取单个用户。

  Args:
    db: SQLAlchemy Session 对象。
    user_id: 要获取的用户的 ID。

  Returns:
    如果找到用户则返回用户模型对象，否则返回 None。
  """
  return db.query(UserModel).filter(UserModel.user_id == user_id).first()


def get_user_by_email(db: Session, email: str) -> Optional[UserModel]:
  """
  通过 email 从数据库中获取单个用户。

  Args:
    db: SQLAlchemy Session 对象。
    email: 要获取的用户的 email。

  Returns:
    如果找到用户则返回用户模型对象，否则返回 None。
  """
  return db.query(UserModel).filter(UserModel.email == email).first()


def get_user_by_username(db: Session, username: str) -> Optional[UserModel]:
  """
  通过 username 从数据库中获取单个用户。

  Args:
    db: SQLAlchemy Session 对象。
    username: 要获取的用户的 username。

  Returns:
    如果找到用户则返回用户模型对象，否则返回 None。
  """
  return db.query(UserModel).filter(UserModel.username == username).first()


def create_user(db: Session, *, user_in: UserCreate) -> UserModel:
  """
  在数据库中创建新用户。

  Args:
    db: SQLAlchemy Session 对象。
    user_in: 包含用户创建信息的 Pydantic schema 对象 (UserCreate)。
             期望 UserCreate 包含 username 字段。

  Returns:
    创建的用户模型对象。
  """
  # User model has `username` which is required.
  # UserCreate inherits UserBase (email, is_active, is_superuser, full_name)
  # and adds `password`.
  # It's assumed UserCreate will be extended to include `username`.
  # If not, user_in.username will raise an AttributeError.
  # The `Users` model does not have `full_name`, `is_active`, `is_superuser` columns.
  # These are present in `UserBase` schema.
  # We should only pass fields to UserModel that exist as columns.
  create_data = {
      "email": user_in.email,
      "username": user_in.username, # Assuming UserCreate has this field
      "hashed_password": get_password_hash(user_in.password),
  }
  # Add optional fields from UserBase if they exist in UserModel (they don't currently)
  # if hasattr(user_in, 'is_active') and user_in.is_active is not None:
  #   create_data['is_active'] = user_in.is_active
  # if hasattr(user_in, 'is_superuser') and user_in.is_superuser is not None:
  #   create_data['is_superuser'] = user_in.is_superuser

  db_obj = UserModel(**create_data)
  db.add(db_obj)
  db.commit()
  db.refresh(db_obj)
  return db_obj


def update_user(
    db: Session, *, db_obj: UserModel, user_in: Union[UserUpdate, Dict[str, Any]]
) -> UserModel:
  """
  更新数据库中的用户信息。

  Args:
    db: SQLAlchemy Session 对象。
    db_obj: 要更新的用户模型对象。
    user_in: 包含用户更新信息的 Pydantic schema 对象 (UserUpdate) 或字典。

  Returns:
    更新后的用户模型对象。
  """
  if isinstance(user_in, dict):
    update_data = user_in
  else:
    update_data = user_in.model_dump(exclude_unset=True) # Pydantic V2

  if "password" in update_data and update_data["password"]:
    hashed_password = get_password_hash(update_data["password"])
    del update_data["password"] # Remove plain password from update_data
    update_data["hashed_password"] = hashed_password # Use password_hash in model
  
  # Ensure we only try to update fields that exist in the model
  # The UserModel currently has: user_id, username, email, password_hash, created_at, updated_at
  # UserUpdate schema inherits UserBase (email, is_active, is_superuser, full_name) and adds password.
  # So, only 'email' and 'password' (which becomes 'hashed_password') are directly applicable.
  # 'username' could be updatable if allowed by UserUpdate schema.
  # 'full_name', 'is_active', 'is_superuser' are not in UserModel.

  for field, value in update_data.items():
    if hasattr(db_obj, field): # Only update if attribute exists in the model
        setattr(db_obj, field, value)
  
  db.add(db_obj)
  db.commit()
  db.refresh(db_obj)
  return db_obj


def delete_user(db: Session, *, user_id: int) -> Optional[UserModel]:
  """
  从数据库中删除用户。

  Args:
    db: SQLAlchemy Session 对象。
    user_id: 要删除的用户的 ID。

  Returns:
    被删除的用户模型对象，如果未找到则返回 None。
  """
  db_obj = db.query(UserModel).get(user_id)
  if db_obj:
    db.delete(db_obj)
    db.commit()
  return db_obj

# 提示: 请确保已安装必要的依赖:
# pip install passlib sqlalchemy
# (python-jose is for security.py)
