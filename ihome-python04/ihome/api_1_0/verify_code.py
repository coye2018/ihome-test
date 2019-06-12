# 该模块用于处理发送给前端的验证码图片


# 引入redis_store
from ihome import redis_store
# 导入redis有效期参数，db：数据库操作类
from ihome import constants,db
from ihome.api_1_0 import api
# 导入captcha包
from ihome.utlis.captcha.captcha import captcha
from flask import current_app,jsonify,make_response,request
# 导入response
from ihome.utlis.response_code import RET,error_map
# 引入数据库模型类
from ihome.models import User
# 引入随机数模块
import random
import json

# 导入云通讯发送短信模块
# from ihome.libs.yunntongxun.sms import CCP

# 引入阿里云通信模块
from ihome.libs.aliyun.ceshi import CCP


# 引入自定义的celery
from ihome.tasks.task_sms import send_sms

# 测试用
@api.route('/image_codes')
def ceshi():
    print(33333)
    return '123'



# GET 127.0.0.1/api/v1.0/image_codes/<image_code_id>
@api.route('/image_codes/<image_code_id>')
def get_image_code(image_code_id):
    '''
    获取图片验证码
    image_code_id:图片验证码编号
    :return: 验证码图片(正常情况下是返回验证码图片)
    异常：返回json
    '''

    #获取参数
    #检验参数

    #名字，真实文本，图片数据
    name,text,image_data=captcha.generate_captcha()


    '''将验证码真实值与编号保存到redis中,设置有效期
    redis：字符串、列表、哈希、set
    "key":xxx
    哈希表可以理解为保存了个字典字典，键和值必须都是字符串
    哈希表的格式
    "image_codes":{"编号1"："真实文本"，"id2"："第二文本"}
    
    在redis中操作
    哈希表的操作
    hset("image_codes","id1","abc")
    获取
    hget("image_codes","id1") 
    获取所有
    HGETALL image_codes
    使用哈希维护有效期的时候只能整体设置
    
    
    单挑维护记录，选用字符串
    "image_code_编号1":"真实值"
    "image_code_编号2":"真实值"
    '''

    #设置键值
    # redis_store.set("image_code_%s"%image_code_id,text)
    #设置有效期
    # redis_store.expire("imgae_code_%s" %image_code_id,IMAGE_CODE_REDIS_EXPIRES)
    # 两步合为一步
    try:
        # IMAGE_CODE_REDIS_EXPIRES是保存的时间
        redis_store.setex("image_code_%s" %image_code_id,constants.IMAGE_CODE_REDIS_EXPIRES,text)
    except Exception as e:
        #记录日志
        current_app.logger.error(e)
        # return jsonify(errno=RET.DBERR,errmsg=error_map[RET.DBERR])
        return jsonify(errno=RET.DBERR, errmsg='保存图片验证码失败')

    # 业务逻辑处理
        #生成验证码图片
        #将验证码真实值与编号保存到redis中
    # 返回图片
    resp=make_response(image_data)
    # 默认是Content-Type:application/json  或者text/html
    resp.headers["Content-Type"]="image/jpg"
    return resp


'''
goods
/add_goods
/update_goods
/delete_goods
/get_goods


/goods
HTTP请求方式
GET 查询
POST 保存
PUT 修改
DELETE 删除


状态码：
200 OK：服务器成功返回用户请求的数据
201 CREATED:用户新建或修改数据成功
202 Accepted：表示请求已进入后台排队
400 INVALID REQUEST:用户发出的请求有错误
401 Unauthorized：用户没有权限
403 Forbidden：访问被精致
404 NOT FOUND:请求针对的是不存在的记录
406 Not Acceptable：用户请求的格式不正确
500 INTERNAL SERVER ERROR:服务器发生错误

'''



#获取验证码
# GET /api/v1.0/sms_codes/<mobile>?image_code=xxxx&image_code_id=xxxx
@api.route("/sms_codes/<re(r'1[345678]\d{9}'):mobile>")
def get_sms_code(mobile):
    """获取短信验证码"""
    #获取参数

    # 就是验证码的文本
    image_code=request.args.get("image_code")
    # 就是那个uuid
    image_code_id=request.args.get("image_code_id")
    #校验参数
    print(image_code,image_code_id)
    if not all([image_code,image_code_id]):
        #表示参数不完整
        return jsonify(errno=RET.PARAMERR,errmsg="参数不完整")
    #业务逻辑处理
    #从redis中取出真实的图片验证码
    try:
        real_image_code=redis_store.get("image_code_%s"%image_code_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="redis数据库异常")


    #判断图片验证码是否过期,因为数据库拿过来的字符串是byte的，要转换为字符串
    print(real_image_code.decode('utf-8'))
    real_image_code=real_image_code.decode('utf-8')
    if real_image_code is None:
        #表示图片验证码没有或者过期
        return jsonify(error=RET.NODATA,errmsg="图片验证码失效")


    #与用户填写的值进行对比(全部转为小写或者大写)
    if real_image_code.lower() != image_code.lower():
        #表示用户填写错误
        return jsonify(error=RET.DATAERR,errmsg="图片验证码错误")


    # 判断对于这个手机号的操作，在60秒内有没有之前的记录，如果有，则认为用户操作频繁，不接受处理
    try:
        send_flag=redis_store.get("send_sms_code_%s"%mobile)
    except Exception as e:
        current_app.logger.error(e)
    else:
        if send_flag is not None:
            #表示60秒内有过发送记录
            return jsonify(errno=RET.REQERR,errmsg="请求过于频繁，请60秒后重试")



    #判断呢手机号是否存在
    try:
        user=User.query.filter_by(mobile=mobile).first()
    except Exception as e:
        current_app.logger.error(e)

    if user is not None:
        #表示手机已经存在了
        return jsonify(errno=RET.DATAEXIST,errmsg="手机号已存在")

    # 删除redis中的图片验证码，防止用户使用同一个图片验证码验证多次
    try:
        redis_store.delete("image_code_%s"%image_code_id)
    except Exception as e:
        # 这里不需要返回
        current_app.logger.error(e)





    #如果手机号不存在，则生成短信验证码
    # sms_code="%6d"%random.randint(0,999999)
    # print(sms_code)
    # print(type(sms_code))

    sms_code = ""
    for i in range(6):
        cssms_code = "%s" % random.randint(0, 9)
        # print(sms_code)
        sms_code = sms_code + cssms_code

    print(sms_code)
    print(type(sms_code))
    #保存真实的短信验证码
    try:
        # 保存300秒
        redis_store.setex("sms_code_%s"%mobile,constants.SMS_CODE_REDIS_EXPIRES,sms_code)
        #保存发送给这个手机号的记录，防止用户在60秒内再次出发发送短信操作,60秒后改为0
        redis_store.setex("send_sms_code_%s"%mobile,constants.SEND_SMS_CODE_INTERVAL,1)
    except Exception as e:
        current_app.logger.error(e)
        redis_store.delete("send_sms_code_%s" % mobile)
        return jsonify(errno=RET.DBERR,errmsg="保存短信验证码异常")




    '''这里准备调用阿里云的短信验证'''
    # 调用第三方也异常判断下
    try:
        #发送短信

        jsonCode={"code":sms_code}
        jsonCode=json.dumps(jsonCode)

        # 因为每天只能发十条不够用所以就默认发出去了
        ccp=CCP(mobile,jsonCode)
        ccp=json.loads(ccp)
        # ccp={'Code':'OK'}

        #(这是云通讯的)手机号码 ，['验证码','有效期'] ， 第三个默认是1
        # result=ccp.send_template_sms(mobile,[sms_code,int(constants.SMS_CODE_REDIS_EXPIRES/60)],1)
        print(ccp)
        print(ccp['Code'])
    except Exception as e:
        current_app.logger.error(e)
        redis_store.delete("send_sms_code_%s" % mobile)
        return jsonify(errno=RET.THIRDERR, errmsg="发送异常")
    # 返回值
    if ccp['Code']=="OK":
        #表示发送成功
        return jsonify(errno=RET.OK,errmsg="短信发送成功")
    else:
        redis_store.delete("send_sms_code_%s" % mobile)
        return jsonify(errno=RET.THIRDERR,errmsg="发送失败")



    '''
    # 使用celey发送短信
    #使用celey异步发送短信，delay函数调用后立刻返回
    jsonCode = {"code": sms_code}
    jsonCode = json.dumps(jsonCode)
    ccp=send_sms.delay(mobile,jsonCode)
    return jsonify(errno=RET.OK, errmsg="短信发送成功")
    '''