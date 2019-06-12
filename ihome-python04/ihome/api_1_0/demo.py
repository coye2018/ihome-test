
from ihome.api_1_0 import api
from flask import current_app

# 视图里面还是需要db的
# from ihome import db,models

# current_app.logger相当于是logging.error('错误级别') #错误级别级别
import logging

@api.route('/index')
def index():
    current_app.logger.error('error info')  #记录错误信息
    current_app.logger.warn('warn info') #警告
    current_app.logger.info('info info')  #信息
    current_app.logger.debug("debug info") #调试
    return 'index page'


# logging.basicConfig(level=logging.ERROR)