启动命令：python3 manage.py runserver
构建数据库：
#init以后会出现一个migrations的文件夹,这个时候versions里面还没有文件，要migrate才有
python author_book.py db init

python author_book.py db migrate
python author_book.py db upgrade

#当把项目转移到别的电脑上用时，通过拿到note.txt中的内容安装虚拟环境
pip3 install -r Environmental.txt
#查看有哪些环境变量
pip list
环境变量：python3.7

alembic==1.0.8
aliyun-python-sdk-core==2.13.4
aliyun-python-sdk-core-v3==2.13.3
amqp==2.4.2
billiard==3.6.0.0
blinker==1.4
celery==4.3.0
certifi==2019.3.9
chardet==3.0.4
Click==7.0
Django==2.2b1
Flask==1.0.2
Flask-Mail==0.9.1
Flask-Migrate==2.4.0
Flask-Script==2.0.6
Flask-Session==0.3.1
Flask-SQLAlchemy==2.3.2
Flask-WTF==0.14.2
gevent==1.4.0
greenlet==0.4.15
gunicorn==19.9.0
idna==2.8
itsdangerous==1.1.0
Jinja2==2.10
jmespath==0.9.4
kombu==4.5.0
Mako==1.0.8
MarkupSafe==1.1.0
Pillow==6.0.0
pycrypto==2.6.1
pycryptodome==3.8.1
pycryptodomex==3.7.2
PyMySQL==0.9.3
python-alipay-sdk==1.10.1
python-dateutil==2.8.0
python-editor==1.0.4
pytz==2018.9
qiniu==7.2.4
redis==3.2.1
requests==2.22.0
six==1.12.0
SQLAlchemy==1.3.2
sqlparse==0.2.4
urllib3==1.25.3
utils==0.9.0
vine==1.3.0
Werkzeug==0.14.1
WTForms==2.2.1
xmltodict==0.12.0
xmltojson==0.2.0
