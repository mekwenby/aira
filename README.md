# AIRA（艾娜）
##### 个人主页，基于Python3.8开发

![1](images/1.webp)


demo:https://aira.030399.xyz/

#### 功能：

- 书签
- 随机数生成
- 密码管理
- 字符串加密
- 日程
- 必应搜索



#### 直接部署：

```bash
# 安装依赖
pip install -r requirements.txt

# 初始化
python init.py

# 运行
uwsgi --ini uwsgi.ini
```



#### Docker:

```bash
# 构建镜像
docker build -f Dockerfile -t mek/aira:1.0 .

# 运行
docker run -d -p 5000:5000 mek/aira:1.0
```
