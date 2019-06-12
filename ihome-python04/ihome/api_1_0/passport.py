
from . import api
from flask import request,jsonify,session,current_app,g
from ihome.utlis.response_code import RET

# python中的正则
import re
# 导入User模型
from ihome.models import User
#  数据库异常具体事项(添加出现错误)
from sqlalchemy.exc import IntegrityError
# 导入redis  # 导入db操作数据库
from ihome import redis_store,db
# 导入生成hash密码和检验hash密码
from werkzeug.security import generate_password_hash,check_password_hash

# 拿到constants里面的常量
from ihome import constants
# 引入判断是否登录装饰器
from ihome.utlis.commons import login_required

# 测试用
@api.route('/paa')
def ceshissss():
    print(33333)
    return "123"

# 注册
# # POST /api/v1.0/users  参数：mobile，sms_code，password，password2
@api.route("/users",methods=["POST"])
def register():
    """
    注册
    请求的参数：手机号、短信验证码、密码
    参数格式：json
    :return:
    """

    #获取请求的json数据，返回字典
    req_dict=request.get_json()
    # 这里拿过来的数据都是字符串
    mobile=req_dict.get("mobile")
    # 短信验证码
    sms_code = req_dict.get("sms_code")
    password = req_dict.get("password")
    password2=req_dict.get("password2")

    # 校验参数
    if not all([mobile,sms_code,password]):
        return jsonify(errno=RET.PARAMERR,errmsg="参数不完整")

    # 判断手机号码格式
    if not re.match(r"1[345678]\d{9}",mobile):
        #表示格式不对
        return jsonify(errno=RET.PARAMERR,errmsg="手机号格式错误")
    if password!=password2:
        return jsonify(errno=RET.PARAMERR,errmsg="两次密码不一致")

    #从redis中取出短信验证码
    try:
        real_sms_code=redis_store.get("sms_code_%s"%mobile)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(erron=RET.DBERR,errmsg="读取真实短信验证码异常")

    #判断短信验证码是否过期
    if not real_sms_code:
        return jsonify(erron=RET.DBERR,errmsg="短信验证码过期")
    #删除redis中的短信验证码，防止重复使用校验
    try:
        redis_store.delete("sms_code_%s"%mobile)
    except Exception as e:
        current_app.logger.error(e)

    real_sms_code=real_sms_code.decode("utf-8")
    print(sms_code,type(sms_code),real_sms_code,type(real_sms_code))
    #判断用户填写短信验证码的正确性
    if str(sms_code) != str(real_sms_code):
        return jsonify(erron=RET.DBERR,errmsg="短信验证码错误")
    #判断用户的手机号是否注册过(其实不用判断，直接添加，有了就无法添加会报错，然后rollback回滚)
    #保存用户的注册数据到数据库中


    # 卡在这里了
    try:
        user=User(name=mobile,mobile=mobile,password=password)

    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno='3',errmsg='添加数据库失败')
    # 这里通过函数直接给User里面的password给赋加密的值
    # user.generate_password_hash(password)
    '''
    如果是user.password=password  是设置属性
        print(user.password)    读取属性
    '''
    # 似乎这种hash加密方式有bug
    # user.password=password

    try:
        db.session.add(user)
        db.session.commit()

    # 假如添加的时候出现重复错误，比如unique的name有了，就会在这行报错
    except IntegrityError as e:
        #数据库操作错误后的回滚
        db.session.rollback()
        #表示手机号出现了重复值，即手机号已经注册过
        current_app.logger.error(e)
        return jsonify(errno=RET.DATAEXIST,errmsg="手机号已存在")
    except Exception as e:
        db.session.rollback()
        #表示手机号出现了别的问题，即手机号已注册过
        current_app.logger.error(e)
        return jsonify(erron=RET.DBERR,errmsg="查询数据库异常")
    #保存登录状态到session中
    session['name']=mobile
    session['mobile']=mobile
    session['user_id']=user.id
    #返回结果
    return jsonify(errno=RET.OK,errmsg="注册成功")



#用户登录
@api.route("/sessions",methods=['POST'])
def login():
    """用户登录
    参数：手机号、密码
    """
    #获取参数
    req_dict=request.get_json()
    mobile=req_dict.get('mobile')
    password=req_dict.get("password")
    print(mobile,password)
    #校验参数
    #参数完整的校验
    if not all([mobile,password]):
        return jsonify(errno=RET.PARAMERR,errmsg='参数不完整')
    # 手机号的格式
    if not re.match(r"1[34578]\d{9}",mobile):
        return jsonify(errno=RET.PARAMERR,errmsg='手机号格式错误')



    #判断错误次数是否超过限制，如果超过限制，则返回
    #redis记录："access_nums_请求的ip"：次数
    user_ip=request.remote_addr  #拿到用户的ip地址
    try:
        # redis数据库的特性决定就算没有存这个进去也会返回一个None
        access_nums=redis_store.get("access_num_%s"%user_ip)
    except Exception as e:
        current_app.logger.error(e)
    else:
        if access_nums is not None and int(access_nums)>=constants.LOGIN_ERROR_MAX_TIMES:
            return jsonify(errno=RET.REQERR,errmsg="错误次数过多，请稍后尝试")



    #从数据库中根据手机号查询用户的数据对象
    try:
        user=User.query.filter_by(mobile=mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="获取用户信息失败")
    #用数据库的密码与用户填写的密码进行对比验证
    print(user,user.password,password,type(user.password),type(password))

    if user is None or user.password!=password:
        #如果验证失败，记录错误次数，返回信息
        try:
            #redis的incr可以对字符串类型的数字数据进行加一操作，如果数据一开始不存在，则初始化为1
            redis_store.incr("access_num_%s"%user_ip)
            redis_store.expire("access_num_%s"%user_ip,constants.LOGIN_ERROR_FORBID_TIME)
        except Exception as e:
            current_app.logger.error(e)
        return jsonify(errno=RET.DATAERR,errmsg="用户名或密码错误")



    #如验证相同成功，保存登录状态，在session中
    session['name']=user.name
    session['mobile']=user.mobile
    session['user_id']=user.id
    return jsonify(errno=RET.OK,errmsg="登陆成功")



# 检查登录状态/api/v1.0/session
@api.route("/session",methods=["GET"])
def check_login():
    """尝试从session中获取用户的名字"""
    name=session.get("name")
    mobile=session.get('mobile')
    user_id=session.get('user_id')
    #如果session中数据name的名字存在，则表示用户已经登录，否则未登录
    if name is not None:
        return jsonify(errno=RET.OK,errmsg="true",data={"name":name,"mobile":mobile,"user_id":user_id})
    else:
        return jsonify(errno=RET.SESSIONERR,errmsg='false')


# 登出
@api.route('/session',methods=['DELETE'])
def logout():
    '''登出'''

    #这里解决一个bug
    csrf_token=session.get("csrf_token")

    #清除session数据,这里会把csrftoken也给一起删除
    session.clear()
    session['csrf_token']=csrf_token
    return jsonify(errno=RET.OK,errmsg='OK')


# 保存用户信息
@api.route('/saveName',methods=['POST'])
@login_required
def saveName():
    user_id=g.user_id
    # user_id=3
    print(user_id)
    name=request.get_json()
    print(name)
    name=name['name']


    if user_id is not None:
        try:
            User.query.filter_by(id=user_id).update({"name":name})
            db.session.commit()
            print(123)
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR,errmsg='保存失败')
        else:
            return jsonify(errno=RET.OK,errmsg='保存成功')
    else:
        return jsonify(errno=RET.DBERR,errmsg='获取用户信息失败')

