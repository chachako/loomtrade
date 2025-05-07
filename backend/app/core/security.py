from datetime import datetime, timedelta, timezone
from typing import Any, Union

from jose import jwt
from passlib.context import CryptContext
from cryptography.fernet import Fernet
import os # 用于从环境变量读取密钥

# JWT 配置
# 建议从环境变量或配置文件中读取这些值
# For demonstration purposes, they are defined here.
# Ensure these are kept secret in a production environment.
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-please-change-this")  # 请务必替换为一个强随机密钥或从环境变量读取
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# API 密钥加密配置
# 重要: 生产环境中绝不能将密钥硬编码在此处！
# 应该从安全的环境变量、配置文件或密钥管理服务 (如 HashiCorp Vault, AWS KMS) 中读取。
# 以下是一个示例密钥，仅用于开发和演示目的。
# 您可以使用以下 Python 代码生成一个新的 Fernet 密钥:
# from cryptography.fernet import Fernet
# key = Fernet.generate_key()
# print(key.decode())
# 将生成的密钥存储在环境变量 `API_ENCRYPTION_KEY` 中。
API_ENCRYPTION_KEY_STR = os.getenv("API_ENCRYPTION_KEY", "your-32-byte-fernet-key-placeholder") # 请替换为真实的 Fernet 密钥
if API_ENCRYPTION_KEY_STR == "your-32-byte-fernet-key-placeholder":
    print("警告: 正在使用占位符 API 加密密钥。请生成并配置一个安全的密钥用于生产环境。")
    # 为了使代码能运行，如果未设置环境变量，我们生成一个临时密钥（不推荐用于生产）
    API_ENCRYPTION_KEY = Fernet.generate_key()
else:
    API_ENCRYPTION_KEY = API_ENCRYPTION_KEY_STR.encode()

try:
    cipher_suite = Fernet(API_ENCRYPTION_KEY)
except Exception as e:
    print(f"错误: 初始化 Fernet 密码套件失败。请检查 API_ENCRYPTION_KEY 是否为有效的 Fernet 密钥。错误: {e}")
    # 提供一个备用方案，以防密钥无效，但这在生产中是不安全的
    print("警告: 由于密钥无效，正在生成临时 Fernet 密钥。这不应用于生产环境。")
    API_ENCRYPTION_KEY = Fernet.generate_key()
    cipher_suite = Fernet(API_ENCRYPTION_KEY)


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def encrypt_api_key(api_key: str) -> str:
    """
    加密 API 密钥。

    Args:
        api_key: 原始 API 密钥字符串。

    Returns:
        加密后的 API 密钥字符串 (bytes 被编码为 utf-8 string)。
    """
    if not api_key:
        return ""
    encrypted_key = cipher_suite.encrypt(api_key.encode())
    return encrypted_key.decode('utf-8')


def decrypt_api_key(encrypted_api_key: str) -> str:
    """
    解密 API 密钥。

    Args:
        encrypted_api_key: 加密后的 API 密钥字符串。

    Returns:
        解密后的原始 API 密钥字符串。
    """
    if not encrypted_api_key:
        return ""
    decrypted_key = cipher_suite.decrypt(encrypted_api_key.encode())
    return decrypted_key.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
  """
  验证普通密码与哈希密码是否匹配。

  Args:
    plain_password: 用户输入的普通密码。
    hashed_password: 数据库中存储的哈希密码。

  Returns:
    如果密码匹配则返回 True，否则返回 False。
  """
  return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
  """
  对普通密码进行哈希处理。

  Args:
    password: 用户输入的普通密码。

  Returns:
    哈希后的密码字符串。
  """
  return pwd_context.hash(password)


def create_access_token(
    subject: Union[str, Any], expires_delta: timedelta = None
) -> str:
  """
  创建 JWT 访问令牌。

  Args:
    subject: 令牌的主题，通常是用户 ID 或 email。
    expires_delta: 可选的 timedelta 对象，用于设置令牌的过期时间。
                   如果未提供，则使用默认的 ACCESS_TOKEN_EXPIRE_MINUTES。

  Returns:
    编码后的 JWT 访问令牌字符串。
  """
  if expires_delta:
    expire = datetime.now(timezone.utc) + expires_delta
  else:
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )
  to_encode = {"exp": expire, "sub": str(subject)}
  encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
  return encoded_jwt

# 提示: 请确保已安装必要的依赖:
# pip install passlib python-jose[cryptography] cryptography