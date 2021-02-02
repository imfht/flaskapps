#! /bin/bash
# 加密密钥
#export SECRET_KE=
# 服务器绑定二级域名 端口 和过滤IP地址设置
#export WEBSERVER_HOST=
#export WEBSERVER_PORT=
export WEBSERVER_ACCESSIP=127.0.0.1
# 注册发送邮件服务器
#export MAIL_SERVE=
#export MAIL_SERVERPORT=
#export MAIL_USERNAME=
#export MAIL_PASSWORD=
#export MAIL_ADDR=
# Database地址
#export DEV_DATABASE_URL=
#export TEST_DATABASE_URL=
#export DATABASE_URL=

python manage.py config
if [ -f "*-nginx.conf" ]; then
    echo "generate nginx conf failed!"
    exit 0
fi
echo "generate nginx conf success!"
if [ -f "*-uwsgi.xml" ]; then
    echo "generate uwsgi conf failed!"
    exit 0
fi
echo "generate uwsgi conf success!"
cp *-nginx.conf /etc/nginx/conf.d/
echo "migrate nginx conf to /etc/nginx/conf.d/....."
/usr/sbin/nginx -s reload
echo "reload nginx....."
uwsgi -x *-uwsgi.xml
echo "success load uwsgi!!!"
