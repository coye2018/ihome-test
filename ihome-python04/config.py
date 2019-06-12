import redis

class Config(object):
    '''配置信息'''
    # DEBUG=True
    SECRET_KEY='EQWEQEQ'

    #数据库
    SQLALCHEMY_DATABASE_URI='mysql+pymysql://root:root@127.0.0.1:8889/author_book_py04'
    #跟随数据库
    SQLALCHEMY_TRACK_MODIFICATIONS=True

    #redis的ip和端口
    REDIS_HOST='127.0.0.1'
    REDIS_PORT='6379'

    #redis的session配置
    SESSION_TYPE="redis"
    SESSION_REDIS=redis.StrictRedis(host=REDIS_HOST,port=REDIS_PORT)
    SESSION_USE_SIGNER=True #对cookie中session_id进行隐藏处理
    PERMANENT_SESSION_LIFETIME=86400  #session数据的有效期，单位秒
    # DEBUG=True
    # FLASK_ENV = 'develop'

# 继承Config然后改变一些东西
class DevelopmentConfig(Config):
    '''开发模式的配置信息'''
    DEBUG = True

class ProductConfig(Config):
    '''生产环境配置信息'''
    pass


# 创建一个映射
config_map={
    "develop":DevelopmentConfig,
    "product":ProductConfig
}