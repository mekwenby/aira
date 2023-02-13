FROM python:3.8.10
COPY . /app
WORKDIR /app
RUN pip3 install -r requirements.txt -i "http://mirrors.aliyun.com/pypi/simple" --trusted-host "mirrors.aliyun.com"
RUN python init.py
EXPOSE 5000
CMD uwsgi --ini uwsgi.ini