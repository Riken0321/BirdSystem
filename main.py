from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from tortoise.contrib.fastapi import register_tortoise
from routers import auth_router, user_router,upload_router,minio_webhook  # 导入所有路由
from middlewares.logging_middleware import log_requests
from middlewares.auth_middleware import authenticate_request
from config import TORTOISE_ORM  # 直接导入

app = FastAPI()

# 配置 CORS
# 调整后的CORS中间件配置（生产环境建议严格限制来源）
# 移除路由级别的CORS配置，统一使用全局中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 临时允许所有来源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# 添加中间件
# 调整中间件顺序
app.middleware("http")(log_requests)  # 日志中间件保持第一

# 添加路由前的调试日志
@app.on_event("startup")
async def startup_event():
    print("已注册路由：", [route.path for route in app.routes])

@app.get("/", include_in_schema=True)
async def read_root():
    return {"message": "Hello World"}
#app.middleware("http")(authenticate_request)

# 注册路由
app.include_router(auth_router.router)
app.include_router(user_router.router)
app.include_router(upload_router.router)
app.include_router(minio_webhook.router)

# 修改Tortoise注册配置源
register_tortoise(
    app,
    config=TORTOISE_ORM,  # 直接使用模块级配置
    generate_schemas=False,# 确保数据库表结构不会被覆盖
    add_exception_handlers=True
)

# 在 FastAPI 中，@app.on_event("startup") 目前并没有被弃用，仍然是标准的启动事件注册方式。
@app.on_event("startup")
async def startup_event():
    """应用启动初始化事件"""