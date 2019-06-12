from . import api
from ihome.utlis.commons import login_required
from ihome.models import Order
from flask import current_app, g, jsonify,request
from ihome.utlis.response_code import RET
from alipay import AliPay
import os
from ihome import constants,db

'''发起支付宝支付'''


#发起支付宝支付
@api.route("/orders/<int:order_id>/payment", methods=["POST"])
@login_required
def order_pay(order_id):
    """发起支付宝支付"""
    user_id = g.user_id

    # 判断订单状态
    try:
        order = Order.query.filter(Order.id == order_id, Order.user_id == user_id, Order.status == "WAIT_PAYMENT").first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库异常")

    if order is None:
        return jsonify(errno=RET.NODATA, errmsg="订单数据有误")

    # 创建支付宝sdk的工具对象
    alipay_client = AliPay(
        appid="2016092800617917",
        app_notify_url=None,  # 默认回调url
        # 下面的string或者path
        app_private_key_path=os.path.join(os.path.dirname(__file__), "keys/app_private_key.pem"),  # 私钥
        alipay_public_key_path=os.path.join(os.path.dirname(__file__), "keys/alipay_public_key.pem"),  # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
        sign_type="RSA2",  # RSA 或者 RSA2
        debug=True  # 默认False
    )

    # 手机网站支付，需要跳转到https://openapi.alipaydev.com/gateway.do? + order_string
    order_string = alipay_client.api_alipay_trade_wap_pay(
        out_trade_no=order.id,  # 订单编号
        total_amount=str(order.amount/100.0),   # 总金额
        subject=u"爱家租房 %s" % order.id,  # 订单标题
        return_url="http://127.0.0.1:5000/payComplete.html",  # 返回的连接地址
        notify_url=None  # 可选, 不填则使用默认notify url
    )

    # 构建让用户跳转的支付连接地址
    pay_url = constants.ALIPAY_URL_PRIFIX + order_string
    return jsonify(errno=RET.OK, errmsg="OK", data={"pay_url": pay_url})


@api.route('/order/payment',methods=["PUT"])
def save_order_payment_result():
    #charset=utf-8&out_trade_no=7&method=alipay.trade.wap.pay.return&total_amount=400.00&sign=g57rQbHVl5OM4GO%2Fo1AhXFZ3LOB8uoZtKhSrx%2BwYV2SMDTRAUZCI5aF0WZTp1bVDObLq1kpQT4X2eL65HYvOKTtQwcG3ibT34muXZ6k0DUI3unTLWuCoAK98o7G1ySJdck0eHakggAL2MZF8fDKeWhoPKBF6nTe1R62%2F1lpjRR5cHRkJUtqjy4NX5r4DZuV0dqwHINoAtyz0%2FBEIIY%2FaBI9PC96rNU5Wnw3Wty90mLGEMcnw20NhsztECx1vnGQBufcG1Ueg%2B2J11HqcDsM1xPPJhWD7mg%2FmEo6uA4UuucPAV6iMpOPGhGSbtNeTvi5EcB%2FKi01cjn3F6PV%2B%2FP7Xxw%3D%3D&trade_no=2019060922001456131000042647&auth_app_id=2016092800617917&version=1.0&app_id=2016092800617917&sign_type=RSA2&seller_id=2088102177691411&timestamp=2019-06-09+15%3A35%3A09
    '''保存订单支付结果'''
    alipay_dict = request.form.to_dict()
    print(alipay_dict)
    #对支付宝的数据进行分离 提取支付宝的签名参数sign，和剩下的其他数据
    alipay_sign = alipay_dict.pop("sign")

    #创建
    alipay_client = AliPay(
        appid="2016092800617917",
        app_notify_url=None,  # 默认回调url
        # 下面的string或者path
        app_private_key_path=os.path.join(os.path.dirname(__file__), "keys/app_private_key.pem"),  # 私钥
        alipay_public_key_path=os.path.join(os.path.dirname(__file__), "keys/alipay_public_key.pem"),
        # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
        sign_type="RSA2",  # RSA 或者 RSA2
        debug=True  # 默认False
    )

    #借助工具验证参数的合法性
    #如果确定参数是支付宝的，返回true
    #result = alipay_client.verify(alipay_dict, alipay_sign)
    #print(result)
    if alipay_sign:
        #修改数据库的订单状态信息
        order_id = alipay_dict.get("out_trade_no")
        trade_no = alipay_dict.get("trade_no")  # 支付宝的交易号
        try:
            Order.query.filter_by(id=order_id).update({"status": "WAIT_COMMENT", "trade_no": trade_no})
            db.session.commit()
        except Exception as e:
            current_app.logger.error(e)
            db.session.rollback()

    return jsonify(errno=RET.OK,errmsg="OK")


