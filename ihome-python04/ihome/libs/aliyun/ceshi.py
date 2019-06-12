#!/usr/bin/env python
#coding=utf-8

from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest
client = AcsClient('LTAI1CUD0JLOtvTB', 'DhHr6I4SLAzTZCYeNKAEBHeQ0vyhq3', 'default')

request = CommonRequest()
request.set_accept_format('json')
request.set_domain('dysmsapi.aliyuncs.com')
request.set_method('POST')
request.set_protocol_type('https') # https | http
request.set_version('2017-05-25')
request.set_action_name('SendSms')


request.add_query_param('SignName', "xcoye")
request.add_query_param('TemplateCode', "SMS_165675464")

# 参数1：电话号码字符串，参数2：json格式字符串'{"code":"123123"}'
def CCP(mobile,json):
    request.add_query_param('TemplateParam', json)
    request.add_query_param('PhoneNumbers', mobile)
    response = client.do_action(request)
    return response



