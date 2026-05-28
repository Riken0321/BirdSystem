from tortoise import fields, models
from tortoise.contrib.pydantic import pydantic_model_creator

# 定义 User 模型，继承自 Tortoise ORM 的 models.Model
class User(models.Model):
    id = fields.IntField(pk=True)  # 主键，用户 ID
    username = fields.CharField(max_length=50, unique=True)  # 用户名，保证唯一
    email = fields.CharField(max_length=100)  # 用户邮箱
    password = fields.CharField(max_length=128)  # 存储哈希后的密码
    created_at = fields.DatetimeField(auto_now_add=True)  # 用户创建时间
    updated_at = fields.DatetimeField(auto_now=True)  # 用户信息更新时间

# 创建 Pydantic 模型，排除 created_at 和 updated_at 字段
User_Pydantic = pydantic_model_creator(User, name="User", exclude=('created_at', 'updated_at', 'password'))
# 用于创建用户时的输入模型，排除只读字段
UserIn_Pydantic = pydantic_model_creator(User, name="UserIn", exclude_readonly=True)