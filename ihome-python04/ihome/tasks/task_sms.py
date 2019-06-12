from celery import Celery
from ihome.libs.aliyun.ceshi import CCP
#定义celery对象(后面的1是指明一号库)
celery_app=Celery("ihome",broker="redis://127.0.0.1:6379/1")


@celery_app.task
def send_sms(mobile,jsondata):
    #发送短信的异步任务
    # 参数1：电话号码字符串，参数2：json格式字符串'{"code":"123123"}'
    ccp=CCP(mobile,jsondata)

# celery -A ihome.tasks.task_sms worker -l info