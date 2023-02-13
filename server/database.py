import time
from peewee import Model, CharField, ForeignKeyField, TextField, DateTimeField, BooleanField, AutoField, fn, chunked
from peewee import IntegerField
import peewee

db = peewee.SqliteDatabase('DATA.db')


class BaseModel(Model):
    class Meta:
        database = db


class User(BaseModel):
    """用户模型"""
    id = AutoField(primary_key=True)
    name = CharField(null=False, index=True, max_length=32)
    passwd = CharField(null=False, max_length=128)
    activation = BooleanField(default=True)  # 是否可用
    Ctime = IntegerField(default=time.time)


class Token(BaseModel):
    """令牌模型,用于Cookie"""
    id = AutoField(primary_key=True)
    link_id = IntegerField(index=True)
    text = CharField(max_length=64)
    Ctime = IntegerField(default=time.time)
    Ftime = IntegerField(null=True)  # 失效时间


class PasswdBox(BaseModel):
    """密码保存盒"""
    id = AutoField(primary_key=True)
    link_id = IntegerField(index=True)
    user = CharField(null=False, index=True, max_length=32)
    passwd = CharField(null=False, max_length=128)
    info = CharField(null=True, max_length=64)
    Ctime = IntegerField(default=time.time)


class PasswdGenerate(BaseModel):
    """密码生成盒"""
    id = AutoField(primary_key=True)
    link_id = IntegerField(index=True)
    user = CharField(null=False, max_length=32)
    passwd = CharField(null=False, max_length=128)
    info = CharField(null=True, max_length=64)
    Ctime = IntegerField(default=lambda: int(time.time()))


class BookMark(BaseModel):
    """书签类"""
    id = AutoField(primary_key=True)
    link_id = IntegerField(index=True)
    url = CharField(max_length=512)
    info = CharField(max_length=512)


class Schedule(BaseModel):
    """日程类"""
    id = AutoField(primary_key=True)
    link_id = IntegerField(index=True)
    text = CharField(max_length=512)
    time = IntegerField(null=True)
    ctime = IntegerField(default=lambda: int(time.time()))


def create_tabls():
    db.create_tables([User, Token, PasswdBox, PasswdGenerate, BookMark, Schedule])
    User.create(name='root', passwd='123456')


if __name__ == '__main__':
    create_tabls()
