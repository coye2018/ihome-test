
# 图片呢验证码的redis有效期,单位秒

IMAGE_CODE_REDIS_EXPIRES=180


# 短信验证码redis有效期，单位秒
SMS_CODE_REDIS_EXPIRES=300

# 发送短信验证码的间隔，单位：秒
SEND_SMS_CODE_INTERVAL=60


# 登录尝试错误次数
LOGIN_ERROR_MAX_TIMES=5


# 登录错误限制的时间 单位是秒
LOGIN_ERROR_FORBID_TIME=600

# 七牛的域名
QINIU_URL_DOMAIN="http://ps1nxwovn.bkt.clouddn.com/"


# 五条数据
HOME_PAGE_MAX_HOUSES=5

# 城区信息的缓存时间，单位：秒
AREA_INFO_REDIS_CACHE_EXPIRES=7200

#首页房屋数据的redis缓存时间，单位秒
HOME_PAGE_DATA_REDIS_EXPIRES=7200
# 房屋列表页面每页数据容量
HOUSE_LIST_PAGE_CAPACITY=2

# 房屋列表页面页数缓存实际，单位秒
HOUSE_LIST_PAGE_REDIS_CACHE_EXPIRES=7200

# 房屋详情页面数据redis缓存时间，单位：秒
HOUSE_DETAIL_REDIS_EXPIRE_SECOND=7200


#房屋详情页面展示的评论最大数
HOUSE_DETAIL_COMMENT_DISPLAY_COUNTS = 30


#支付宝网关地址（支付地址域名）(沙箱测试环境)
ALIPAY_URL_PRIFIX="https://openapi.alipaydev.com/gateway.do?"