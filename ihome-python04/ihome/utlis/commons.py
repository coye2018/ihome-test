from werkzeug.routing import BaseConverter
from flask import session,jsonify,g
from ihome.utlis.response_code import RET
# python提供的标准模块
import functools

# 定义正则转换器
class ReConverter(BaseConverter):
    ''''''
    def __init__(self,url_map,regex):
        #调用父类的初始化方法
        super(ReConverter,self).__init__(url_map)
        #保存正则表达式
        self.regex=regex


# 定义验证登录状态的装饰器
def login_required(view_func):
    @functools.wraps(view_func)
    def wrapper(*args,**kwargs):
        #判断用户的登录状态
        user_id=session.get("user_id")
        if user_id is not None:
            # 将user_id保存到g对象中，在试图函数中能够可以通过g对象获取保存数据
            g.user_id=user_id
            # 带括号表示装饰的时候调用了一次原函数
            return view_func(*args,**kwargs)

        else:
            # 如果为登录，返回未登录的信息
            return jsonify(errno=RET.SESSIONERR,errmsg="用户未登录")
    return wrapper

# 例子
'''
@login_required
def xxx():
    return 'xxxxx'
'''