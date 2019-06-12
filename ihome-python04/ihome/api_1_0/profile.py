
from . import api
from ihome.utlis.commons import login_required
from flask import g,current_app,jsonify,request
from ihome.utlis.response_code import RET
from ihome.utlis.image_storages import storage
from ihome.models import User
from ihome import db,constants
# 引入七牛保存图片根域名
from ihome.constants import QINIU_URL_DOMAIN


# 设置图片
@api.route("/users/avatar",methods=["POST"])
@login_required  #装饰器,先把装饰器注释掉
def set_user_acatar():
    #设置用户的头像
    '''
    参数：图片(多媒体表单格式) 用户id（g.user_id）
    :return:
    '''

    #装饰器的代码中已经将user_id保存到g对象中，所以试图中可以直接读取
    # 这个在commons里面的验证登录的装饰器里面存储
    user_id=g.user_id
    # user_id=3

    #获取图片(这个传过来的一定是二进制)
    image_file=request.files.get("avatar")

    print("这是图片：",image_file,type(image_file))

    if image_file is None:
        return jsonify(errno=RET.PARAMERR,errmsg="未上传图片")

    #读取文件数据
    image_data=image_file.read()

    #调用七牛上传图片
    try:
        filename=storage(image_data)
    except Exception as e:
        # 失败的话铺货自己写的异常
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR,errmsg="上传图片失败")

    # 图片的地址为 七牛云的控制台可以查询  ps1nxwovn.bkt.clouddn.com/filename
    #把filename存入数据库
    try:
        User.query.filter_by(id=user_id).update({"avatar_url":filename})
        #如果有了直接commit就行了
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="保存图片信息失败")

    #拼接完整图片链接地址
    avatar_url=QINIU_URL_DOMAIN+filename
    #保存成功返回
    return jsonify(errno=RET.OK,errmsg="保存成功",data={"avatar_url":avatar_url})


# 获取头像图片,顺便获取用户名
@api.route('/users/avatarJc',methods=['POST'])
@login_required
def get_userImg():
    user_id = g.user_id
    print(user_id)

    if user_id is None:
        return jsonify(errno=RET.DBERR, errmsg="请登录")

    # 从数据库里面拿图片的值
    try:
        user=User.query.filter_by(id=user_id).first()

    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="获取用户信息失败")

    print(123)
    print(user.avatar_url)
    if user.avatar_url is not None:
        url=QINIU_URL_DOMAIN+user.avatar_url
        return jsonify(errno=RET.OK,data={"avatar_url":url,'name':user.name})
    else:
        return jsonify(errno=RET.DBERR,errmsg="返回失败")



# 在my页面获取用户信息
@api.route('/user',methods=['GET'])
@login_required
def get_user_profile():
    user_id=g.user_id
    try:
        user=User.query.filter_by(id=user_id).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="数据库出错")

    if user is None:
        return jsonify(errno=RET.NODATA,errmsg="无效操作")
    data={
        'name':user.name,
        'mobile':user.mobile,
        'avatar_url':constants.QINIU_URL_DOMAIN+user.avatar_url
    }
    return jsonify(errno=RET.OK,errmsg="OK",data=data)



# 获取用户的实名认证 /api/v1.0/users/auth
@api.route('/users/auth',methods=["GET"])
@login_required
def get_user_auth():
    '''
    真实姓名：real_name   身份证号码：id_card
    :return:
    '''
    user_id=g.user_id
    try:
        user=User.query.filter_by(id=user_id).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="获取数据库信息异常")

    if not user:
        return jsonify(errno=RET.DBERR,errmsg="没有数据")

    # 判断有没有在前端好了只要返回real_name和id_card就行了
    data={
        'real_name':user.real_name,
        'id_card':user.id_card
    }
    return jsonify(errno=RET.OK,data=data)


# 保存用户实名认证信息
@api.route('/users/auth',methods=["POST"])
@login_required
def save_user_auth():
    user_id=g.user_id
    print(user_id)

    getData=request.get_json()
    real_name=getData.get('real_name')
    id_card=getData.get('id_card')
    try:
        user=User.query.filter_by(id=user_id).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="获取数据库信息失败")

    if not all([real_name,id_card]):
        return jsonify(errno=RET.DBERR,errmsg="传过来的数据不全")
    #更新数据库
    try:
        user.real_name=real_name
        user.id_card=id_card
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR,errmsg="数据更新失败")


    return jsonify(errno=RET.OK,errmsg="更新成功")
