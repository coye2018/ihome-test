from ihome.tasks.main import celery_app
from ihome.libs.aliyun.ceshi import CCP


@celery_app.task
def send_sms(mobile,jsondata):
    # 发送短信的异步任务
    ccp=CCP(mobile,jsondata)
    return ccp

