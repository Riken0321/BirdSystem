from fastapi import FastAPI, HTTPException, Depends, status,Request
import logging
import time
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta

from utils.log_config import setup_logging
from backend.models.models import User, User_Pydantic, UserIn_Pydantic
from tortoise.contrib.fastapi import register_tortoise
from tortoise.exceptions import DoesNotExist
from utils.auth import authenticate_user, create_access_token, get_current_user, get_password_hash
from fastapi.responses import JSONResponse
from routers.camera_router import router as camera_router
from routers.bird_species_router import router as bird_species_router

# 创建 FastAPI 应用实例
app = FastAPI()

# 配置日志记录
setup_logging()
# 获取 requests 分类的日志记录器
logger = logging.getLogger("requests")
'''
#日志中间件
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    # 使用 requests 分类的日志记录器记录请求信息
    logger.info(f"Request received: {request.method} {request.url}")
    try:
        response = await call_next(request)
    except Exception as e:
        # 记录异常信息
        logger.error(f"An error occurred during request processing: {e}")
        raise
    process_time = (time.time() - start_time) * 1000
    formatted_process_time = '{0:.2f}'.format(process_time)
    # 记录响应信息和处理时间
    logger.info(f"Request completed in {formatted_process_time}ms. Status code: {response.status_code}")
    return response
    
    #认证中间件   
@app.middleware("http")
async def authenticate_request(request: Request, call_next):
    # 可以根据需要排除某些不需要认证的路径
    excluded_paths = ["/", "/token","/docs"]
    if request.url.path in excluded_paths:
        return await call_next(request)
    try:
        token = request.headers.get("Authorization")
        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication token is missing",
                headers={"WWW-Authenticate": "Bearer"},
            )
        token = token.replace("Bearer ", "")
        # 调用认证函数验证令牌
        await get_current_user(token)
    except HTTPException as e:
        return JSONResponse(
            status_code=e.status_code,
            content={"detail": e.detail},
            headers=e.headers
        )
    return await call_next(request)
'''

# 注册 Tortoise ORM
register_tortoise(
    app,
    db_url='mysql://root:123456@localhost/mydatabase',  # 根据实际情况修改数据库连接字符串
    modules={'models': ['backend.models.models']},  # 确保模块路径正确
    generate_schemas=True, # 自动生成数据库表结构
    add_exception_handlers=True # 自动添加异常处理程序
)

"""根路由测试接口"""
@app.get("/")
async def read_root():
    return {"message": "Hello World"}

# 登录接口
@app.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# 受保护的路由示例
@app.get("/protected")
async def protected_route(current_user: User_Pydantic = Depends(get_current_user)):
    return {"message": f"Hello, {current_user.username}! This is a protected route."}

# 创建用户，需要认证
@app.post("/users/", response_model=User_Pydantic)
async def create_user(user: UserIn_Pydantic):
    hashed_password = get_password_hash(user.password)
    user_obj = await User.create(**user.dict(exclude={"password"}), password=hashed_password)
    return await User_Pydantic.from_tortoise_orm(user_obj)

# 查询所有用户
@app.get("/users/", response_model=list[User_Pydantic])
async def get_all_users():
    users_queryset = User.all()  # 不提前执行 await，保留 QuerySet 对象
    return await User_Pydantic.from_queryset(users_queryset)

# 根据 ID 查询用户
@app.get("/users/{user_id}", response_model=User_Pydantic, status_code=200)
async def get_user_by_id(user_id: int):
    try:
        user = await User.get(id=user_id)
        return await User_Pydantic.from_tortoise_orm(user)
    except DoesNotExist:  # 捕获 DoesNotExist 异常
        raise HTTPException(status_code=404, detail="User not found")

# 更新用户信息
@app.put("/users/{user_id}", response_model=User_Pydantic)
async def update_user(user_id: int, user: UserIn_Pydantic, current_user: User_Pydantic = Depends(get_current_user)):
    try:
        user_obj = await User.get(id=user_id)
        user_data = user.dict(exclude_unset=True)
        if "password" in user_data:
            user_data["password"] = get_password_hash(user_data["password"])
        for key, value in user_data.items():
            setattr(user_obj, key, value)
        await user_obj.save()
        return await User_Pydantic.from_tortoise_orm(user_obj)
    except DoesNotExist:
        raise HTTPException(status_code=404, detail="User not found")

# 删除用户
@app.delete("/users/{user_id}")
async def delete_user(user_id: int, current_user: User_Pydantic = Depends(get_current_user)):
    try:
        user_obj = await User.get(id=user_id)
        await user_obj.delete()
        return {"message": "User deleted successfully"}
    except DoesNotExist:
        raise HTTPException(status_code=404, detail="User not found")

app.include_router(camera_router)
app.include_router(bird_species_router)