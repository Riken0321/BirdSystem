from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from tortoise.exceptions import DoesNotExist
from models.models import User, User_Pydantic
from datetime import timezone

# 创建密码哈希上下文，使用bcrypt算法进行密码加密
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT相关配置
SECRET_KEY = "your-secret-key"  # JWT加密密钥，生产环境应使用随机生成的密钥
ALGORITHM = "HS256"  # JWT加密算法
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # 访问令牌过期时间（分钟）

# 创建OAuth2密码授权方案，指定token获取的URL端点
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_password(plain_password, hashed_password):
    """验证密码是否正确
    
    Args:
        plain_password: 明文密码
        hashed_password: 哈希后的密码
        
    Returns:
        bool: 密码是否匹配
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    """获取密码的哈希值
    
    Args:
        password: 明文密码
        
    Returns:
        str: 哈希后的密码
    """
    return pwd_context.hash(password)

async def get_user(username: str):
    """根据用户名获取用户信息
    
    Args:
        username: 用户名
        
    Returns:
        User: 用户对象，如果用户不存在则返回None
    """
    try:
        user = await User.get(username=username)
        return user
    except DoesNotExist:
        return None

async def authenticate_user(username: str, password: str):
    """验证用户身份
    
    Args:
        username: 用户名
        password: 密码
        
    Returns:
        User/bool: 如果验证成功返回用户对象，失败返回False
    """
    user = await get_user(username)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """创建访问令牌
    
    Args:
        data: 要编码到令牌中的数据
        expires_delta: 过期时间增量，如果未指定则默认15分钟
        
    Returns:
        str: JWT令牌字符串
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    """获取当前登录用户
    
    Args:
        token: JWT令牌，通过依赖注入获取
        
    Returns:
        User_Pydantic: 当前登录用户的Pydantic模型
        
    Raises:
        HTTPException: 当令牌验证失败时抛出401未授权异常
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # 解码JWT令牌
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    # 获取用户信息
    user = await get_user(username=username)
    if user is None:
        raise credentials_exception
    return await User_Pydantic.from_tortoise_orm(user)