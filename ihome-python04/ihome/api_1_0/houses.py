

from . import api
from flask import g,current_app,jsonify,request,session
from ihome.utlis.response_code import RET
from ihome.utlis.image_storages import storage

# 引入用户，城区,房屋，设施信息
from ihome.models import User,Area,House,Facility,HouseImage,Order,house_facilyty
from ihome import db,constants,redis_store

# 引入判断是否登录装饰器
from ihome.utlis.commons import login_required

import json
# 获取七牛上传图片
from ihome.utlis.image_storages import storage
#获取时间模块
from datetime import datetime


# 缓存使用redis或者全局变量，建议redis
@api.route('/areas',methods=['GET'])
def get_area_info():
    """获取城区信息"""

    # 一上来先尝试从redis中读取数据
    try:
        resp_json=redis_store.get("area_info")
    except Exception as e:
        current_app.logger.error(e)
    else:
        if resp_json is not None:
            #表示有缓存数据,redis拿过来的数据是转换成json字符串的
            current_app.logger.info("hit redis area_info")
            return resp_json, 200, {"Content-Type": "application/json"}

    #查询数据库，读取城区信息
    try:
        area_li=Area.query.all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="数据库异常")

    # 把取出来的城区数据转换为字典
    # 定义一个存储的列表
    area_dict_li=[]
    for area in area_li:
        d={
            "aid":area.id,
            "aname":area.name
        }
        area_dict_li.append(d)


    # 将数据转换为json字符串,用函数的方式创建字典
    resp_dict=dict(errno=RET.OK,errmsg="OK",data=area_dict_li)
    resp_json=json.dumps(resp_dict)
    #  将数据保存到redis数据库
    try:
        # 这里一定要设置有效期
        redis_store.setex("area_info",constants.AREA_INFO_REDIS_CACHE_EXPIRES,resp_json)
    except Exception as e:
        current_app.logger.error(e)

    # 上面已经转换一次了
    # return jsonify(errno=RET.OK,errmsg="OK",data=area_dict_li)
    return resp_json,200,{"Content-Type":"application/json"}



# 保存房屋的信息
@api.route('/houses/info',methods=["POST"])
@login_required
def save_house_info():
    """前端发送过来的json数据
    {
        "title":"",
        "price":"",
        "area_id":"1",
        "address":"",
        "room_count":"",
        "acreage":"",
        "unit":"",
        "capacity":"",
        "beds":"",
        "deposit":"",
        "min_days":"",
        "max_days":"",
        "facility":["7","8"]
        }
    """

    # 获取数据
    user_id = g.user_id
    house_data = request.get_json()

    title = house_data.get("title")  # 房屋名称标题
    price = house_data.get("price")  # 房屋单价
    area_id = house_data.get("area_id")  # 房屋所属城区的编号
    address = house_data.get("address")  # 房屋地址
    room_count = house_data.get("room_count")  # 房屋包含的房间数目
    acreage = house_data.get("acreage")  # 房屋面积
    unit = house_data.get("unit")  # 房屋布局（几室几厅)
    capacity = house_data.get("capacity")  # 房屋容纳人数
    beds = house_data.get("beds")  # 房屋卧床数目
    deposit = house_data.get("deposit")  # 押金
    min_days = house_data.get("min_days")  # 最小入住天数
    max_days = house_data.get("max_days")  # 最大入住天数

    # 校验参数
    if not all([title, price, area_id, address, room_count, acreage, unit, capacity, beds, deposit, min_days, max_days]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不完整")


    #判断金额是否正确
    try:
        price=int(float(price)*100)
        deposit=int(float(deposit)*100)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR,errmsg="参数错误")


    #判断城区id是否存在
    try:
        area=Area.query.get(area_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="数据库异常")

    if area is None:
        return jsonify(errno=RET.NODATA,errmsg="城区信息有误")

        # 保存房屋信息
    house = House(
        user_id=user_id,
        area_id=area_id,
        title=title,
        price=price,
        address=address,
        room_count=room_count,
        acreage=acreage,
        unit=unit,
        capacity=capacity,
        beds=beds,
        deposit=deposit,
        min_days=min_days,
        max_days=max_days
    )

    #处理房屋的设施信息
    facility_ids=house_data.get("facility")

    #如果勾选了设施信息，再保存数据库
    if facility_ids:
        #["7","8"]
        try:
            facilities=Facility.query.filter(Facility.id.in_(facility_ids)).all()
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR,errmsg="数据库异常")

        if facilities:
            #表示有合法的设施数据
            #保存设施数据
            #这个是保存到中间表去的
            house.facilities=facilities

    #推送上去
    try:
        db.session.add(house)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="保存数据失败")


    #保存数据成功
    return jsonify(errno=RET.OK,errmsg="OK",data={"house_id":house.id})



# 保存房屋的图片
@api.route('/houses/image',methods=["POST"])
@login_required
def save_house_image():
    '''参数：图片 房屋id'''
    image_file=request.files.get('house_image')
    house_id=request.form.get("house_id")

    if not all([image_file,house_id]):
        return jsonify(errno=RET.PARAMERR,errmsg="参数错误")

    #判断house_id正确性
    try:
        house=House.query.get(house_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库异常")

    if house is None:  # if not house:
        return jsonify(errno=RET.NODATA, errmsg="房屋不存在")

    image_data=image_file.read()

    #保存图片到七牛中
    try:
        file_name=storage(image_data)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR, errmsg="保存图片失败")

    #保存图片到数据库中(一个专门存图片的数据库)
    house_image= HouseImage(house_id=house_id,url=file_name)
    db.session.add(house_image)

    #处理房屋的主图片(如果house里面有url地址就不用加了，只要给house_image表加就可以)
    if not house.index_image_url:
        house.index_image_url = file_name
        db.session.add(house)

    try:
        # 其实是把house info的url和house_image的url都保存了
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="保存图片数据异常")

    image_url = constants.QINIU_URL_DOMAIN + file_name

    return jsonify(errno=RET.OK, errmsg="OK", data={"image_url": image_url})



# 把数据库对象转换为想要的字典
def to_basic_dict(value):

    house_dict = {
        "house_id": value.id,
        "title": value.title,
        "price": value.price,
        "area_name": value.area_id,
        "img_url": constants.QINIU_URL_DOMAIN + value.index_image_url if value.index_image_url else "",
        "room_count": value.room_count,
        "order_count": value.order_count,
        "address": value.address,

        # "user_avatar": constants.QINIU_URL_DOMAIN + value.user.avatar_url if value.user.avatar_url else "",
        "user_avatar":constants.QINIU_URL_DOMAIN + User.query.get(value.user_id).avatar_url if value.user_id else "",
        "ctime": value.create_time.strftime("%Y-%m-%d")
    }
    return house_dict
'''获取主页幻灯片展示的房屋基本信息'''
'''
house_dict = {
            "house_id": self.id,
            "title": self.title,
            "price": self.price,
            "area_name": self.area.name,
            "img_url": constants.QINIU_URL_DOMAIN + self.index_image_url if self.index_image_url else "",
            "room_count": self.room_count,
            "order_count": self.order_count,
            "address": self.address,
            "user_avatar": constants.QINIU_URL_DOMAIN + self.user.avatar_url if self.user.avatar_url else "",
            "ctime": self.create_time.strftime("%Y-%m-%d")
        }
'''
@api.route('/houses/index',methods=['GET'])
def get_house_index():

    #从缓存中尝试获取数据
    try:
        #这个ret是图片字符串
        ret=redis_store.get("home_page_data")
    except Exception as e:
        current_app.logger.error(e)
        ret=None

    if ret:
        current_app.logger.info("hit house index info redis")
        #因为redis中保存的是json字符串，所以直接进行字符串拼接返回
        #ret是二进制数据，要转字符串
        ret=ret.decode('utf-8')
        # print(ret)
        return '{"errno":0,"errmsg":"OK","data":%s}'%ret,200,{"Content-Type":"application/json"}
    else:

        try:
            #查询数据库，返回房屋订单数目最多的五条数据
            houses=House.query.order_by(House.order_count.desc()).limit(constants.HOME_PAGE_MAX_HOUSES)
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR,errmsg="查询数据失败")

        if not houses:
            return jsonify(errno=RET.NODATA,errmsg="查询无数据")


        houses_list=[]

        for house in houses:
            if not house.index_image_url:
                continue
            houses_list.append(to_basic_dict(house))

        #将数据转换为json，并保存到redis缓存
        json_houses=json.dumps(houses_list)  #"[{},{},{}]"
        try:
            redis_store.setex("home_page_data",constants.HOME_PAGE_DATA_REDIS_EXPIRES,json_houses)
        except Exception as e:
            current_app.logger.error(e)

        return '{"erron":0,"errmsg":"OK","data":%s}'%json_houses,200,{"Content-Type":"application/json"}



#将详细信息转换为字典数据
def to_full_dict(value):
    """将详细信息转换为字典数据"""
    house_dict = {
        "hid": value.id,
        "user_id": value.user_id,
        "user_name": User.query.get(value.user_id).name,
        "user_avatar": constants.QINIU_URL_DOMAIN + User.query.get(value.user_id).avatar_url if User.query.get(value.user_id).avatar_url else "",
        "title": value.title,
        "price": value.price,
        "address": value.address,
        "room_count": value.room_count,
        "acreage": value.acreage,
        "unit": value.unit,
        "capacity": value.capacity,
        "beds": value.beds,
        "deposit": value.deposit,
        "min_days": value.min_days,
        "max_days": value.max_days,
    }

    # 房屋图片
    img_urls = []
    houseImg=HouseImage.query.filter_by(house_id=value.id).all()
    for image in houseImg:
        img_urls.append(constants.QINIU_URL_DOMAIN + image.url)
    house_dict["img_urls"] = img_urls

    # 房屋设施
    #返回的是facility_id
    facilities = []
    facils=value.facilities
    for facility in facils:
        facilities.append(facility.id)
    house_dict["facilities"] = facilities

    # 评论信息

    comments = []
    orders = Order.query.filter(Order.house_id == value.id, Order.status == "COMPLETE", Order.comment != None) \
        .order_by(Order.update_time.desc()).limit(constants.HOUSE_DETAIL_COMMENT_DISPLAY_COUNTS)
    for order in orders:
        comment = {
            "comment": order.comment,  # 评论的内容
            "user_name": User.query.get(order.user_id).name if User.query.get(order.user_id).name != User.query.get(order.user_id).mobile else "匿名用户",  # 发表评论的用户
            "ctime": order.update_time.strftime("%Y-%m-%d %H:%M:%S")  # 评价的时间
        }
        comments.append(comment)
    house_dict["comments"] = comments


    return house_dict
'''获取详情页面信息'''
@api.route('/houses/<int:house_id>',methods=['GET'])
def get_house_detail(house_id):

    '''获取房屋详情'''
    #前端在房屋详情页面展示时，如果浏览页面的用户不是该烦那房屋的房东，则展示确定按钮，否则不展示
    #所以需要后端返回登录用户的user_id
    #尝试获取用户登录信息，若登录，则返回给前端用户user_id，否则返回user_id=-1
    user_id=session.get('user_id','-1')


    #校验参数
    if not house_id:
        return jsonify(errno=RET.PARAMERR,errmsg='木有参数')
    #先从redis缓存中获取信息
    try:
        ret=redis_store.get("house_info_%s"%house_id)
    except Exception as e:
        current_app.logger.error(e)
        ret=None


    if ret:
        ret=ret.decode('utf-8')
        current_app.logger.info("hit house info redis")
        return '{"errno":"0","errmsg":"OK","data":{"user_id":%s,"house":%s}}'%(user_id,ret),200,{"Content-Type":"application/json"}

    #查询数据库
    try:
        house=House.query.get(house_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="查询数据失败")

    if not house:
        return jsonify(errno=RET.NODATA,errmsg="房屋不存在")

    #将房屋对象数据转换为字典
    try:
        house_data=to_full_dict(house)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DATAERR,errmsg="数据出错")

    #存入到redis中
    print(house_data)
    json_house=json.dumps(house_data)
    try:
        redis_store.setex("house_info_%s"%house_id,constants.HOUSE_DETAIL_REDIS_EXPIRE_SECOND,json_house)
    except Exception as e:
        current_app.logger.error(e)

    return '{"errno":"0","errmsg":"OK","data":{"user_id":%s,"house":%s}}' % (user_id, json_house),200 , {"Content-Type":"application/json"}



"""获取房屋的列表信息（搜索页面）"""
# GET /api/v1.0/houses?sd=2017-12-01&ed=2017-12-31&aid=10&sk=new&p=1
@api.route('/houses')
def get_house_list():
    """获取房屋的列表信息（搜索页面）"""
    start_date=request.args.get("sd","")#用户想要的起始时间
    end_date=request.args.get("ed","") #用户想要的结束时间
    area_id=request.args.get('aid',"")#区域编号
    sort_key=request.args.get('sk','new')  #排序关键字,如果没选默认就是new
    page=request.args.get('p')  #页数

    print(sort_key)

    #处理时间
    try:
        if start_date:
            start_date=datetime.strptime(start_date,"%Y-%m-%d")

        if end_date:
            end_date = datetime.strptime(end_date, "%Y-%m-%d")

        if start_date and end_date:
            assert start_date<=end_date
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR,errmsg="日期参数有误")


    #判断区域id
    if area_id:
        try:
            area=Area.query.get(area_id)
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.PARAMERR, errmsg="区域参数有误")

    #处理页数
    try:
        page=int(page)
    except Exception as e:
        current_app.logger.error(e)
        page=1


    #获取缓存数据
    redis_key="house_%s_%s_%s_%s"%(start_date,end_date,area_id,sort_key)
    try:
        resp_json=redis_store.hget(redis_key,page)
    except Exception as e:
        current_app.logger.error(e)
    else:
        if resp_json:#这里获取到的是可以直接发送回前端的数据，如果是自己要用就要decode转码
            return resp_json,200,{'Content-Type':'application/json'}


    #过滤条件的参数列表容器
    filter_params=[]

    #填充过滤参数
    #时间条件
    conflict_orders=None

    #查询冲突的订单，三种模式
    #1、start和end都有 2、只有start 3、只有end
    try:
        if start_date and end_date:
            conflict_orders=Order.query.filter(Order.begin_date<=end_date,Order.end_date>=start_date).all()
        elif start_date:
            conflict_orders=Order.query.filter(Order.end_date>=start_date).all()
        elif end_date:
            conflict_orders = Order.query.filter(Order.begin_date <=end_date).all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="数据库异常")


    if conflict_orders:
        #从订单中获取冲突的房屋id
        # 得到的是一个列表
        conflict_house_ids=[order.house_id for order in conflict_orders]

        #如果冲突的房屋id不为空，向查询参数中添加条件
        if conflict_house_ids:
            filter_params.append(House.id.notin_(conflict_house_ids))


    #区域条件
    if area_id:
        #这样相当于里面有了[House.area_id==area_id,House.id.notin_(conflict_house_ids)]
        filter_params.append(House.area_id==area_id)
        #看一下到底append个啥玩意
        print(filter_params)

    #查询数据库
    #补充排序条件
    if sort_key=="booking": #入住最多
        house_query=House.query.filter(*filter_params).order_by(House.order_count.desc())
        print("booking")
    elif sort_key=='price-inc': #价格低到高
        print("price-inc")
        house_query=House.query.filter(*filter_params).order_by(House.price.asc())
    elif sort_key=='price-des': #价格高到低
        print("price-des")
        house_query = House.query.filter(*filter_params).order_by(House.price.desc())
    else: #最新
        print("new")
        house_query = House.query.filter(*filter_params).order_by(House.update_time.desc())


    #处理分页
    try:
        #page：当前页数、per_page：每页数据量、error_out：自动的错误输出
        page_obj=house_query.paginate(page=page,per_page=constants.HOUSE_LIST_PAGE_CAPACITY,error_out=False)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="数据库异常")

    #获取页面数据 page_obj只拿到了前两条
    print('page_obj',page_obj)
    # 分页后的一个属性，返回当前页的所有数据
    house_li=page_obj.items
    print('house_li',house_li)
    houses=[]
    for house in house_li:
        houses.append(to_basic_dict(house))


    #获取总页数
    total_page=page_obj.pages

    resp_dict=dict(errno=RET.OK,errmsg="OK",data={"total_page":total_page,"houses":houses,"current_page":page})
    resp_json=json.dumps(resp_dict)


    if page<=total_page:
        #设置缓存数据
        redis_key="house_%s_%s_%s_%s"%(start_date,end_date,area_id,sort_key)
        #哈希类型
        try:
            # redis_store.hset(redis_key, page, resp_json)
            # redis_store.expire(redis_key, constants.HOUES_LIST_PAGE_REDIS_CACHE_EXPIRES)

            # 创建redis管道对象，可以一次执行多个语句
            pipeline=redis_store.pipeline()
            #开启多个语句的记录
            pipeline.multi()

            pipeline.hset(redis_key,page,resp_json)
            pipeline.expire(redis_key,constants.HOUSE_LIST_PAGE_REDIS_CACHE_EXPIRES)

            #执行语句
            pipeline.execute()
        except Exception as e:
            current_app.logger.error(e)


    return resp_json,200,{'Content-Type':'application/json'}


# redis_store
#
# "house_起始_结束_区域id_排序_页数"
# (errno=RET.OK, errmsg="OK", data={"total_page": total_page, "houses": houses, "current_page": page})
#
#
#
# "house_起始_结束_区域id_排序": hash
# {
#     "1": "{}",
#     "2": "{}",
# }