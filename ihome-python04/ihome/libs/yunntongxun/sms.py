# coding=utf-8


from .CCPRestSDK import REST
# from .CCPRestSDK import REST
# import ConfigParser

#主帐号
accountSid= '8a216da86a43ea63016a57488f381465'

#主帐号Token
accountToken= '001010687eec4bd693d686b8862d0875'

#应用Id
appId='8a216da86a43ea63016a57488f90146c'

#请求地址，格式如下，不需要写http://
serverIP='app.cloopen.com'

#请求端口 
serverPort='8883'

#REST版本号
softVersion='2013-12-26'

  # 发送模板短信
  # @param to 手机号码
  # @param datas 内容数据 格式为数组 例如：{'12','34'}，如不需替换请填 ''
  # @param $tempId 模板Id

# 自己定义一个发送短信
class CCP(object):
    # 用来保存对象的类属性
    instance=None

    """自己封装的发送短信的辅助类"""
    def __new__(cls, *args, **kwargs):
        """判断ccp类有没有已经创建好的对象，如果没有，创建一个对象，并且保存"""
        #如果有，则将保存的对象直接返回
        if cls.instance is None:
            #cls表示类，类似self
            obj=super(CCP,cls).__new__(cls)
            #初始化REST SDK
            obj = REST(serverIP, serverPort, softVersion)
            obj.setAccount(accountSid, accountToken)
            obj.setAppId(appId)

            cls.instance=obj
        return cls.instance

    def send_template_sms(self,to, datas, tempId):
        # 初始化REST SDK
        # rest = REST(serverIP,serverPort,softVersion)
        # rest.setAccount(accountSid,accountToken)
        # rest.setAppId(appId)

        result = self.rest.sendTemplateSMS(to, datas, tempId)
        # for k,v in result.iteritems():
        #
        #     if k=='templateSMS' :
        #             for k,s in v.iteritems():
        #                 print ('%s:%s' % (k, s))
        #     else:
        #         print ('%s:%s' % (k, v))
        status_code=result.get("statusCode")
        if status_code=="000000":
            #表示发送短信成功
            return 0
        else:
            #发送失败
            return -1

#sendTemplateSMS(手机号码,内容数据,模板Id)



ccp=CCP()
# 测试的datas和模板id固定了
ret=ccp.send_template_sms("18770012640",["1234",5],1)
print(ret)