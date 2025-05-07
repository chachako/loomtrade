from typing import Optional

from pydantic import BaseModel


class Token(BaseModel):
  """
  表示 JWT 访问令牌的 Pydantic schema。
  """
  access_token: str
  token_type: str


class TokenData(BaseModel):
  """
  表示 JWT 令牌中存储的数据的 Pydantic schema。
  通常包含用户标识（如用户名或 ID）。
  """
  username: Optional[str] = None # 在我们的例子中，这通常是 email