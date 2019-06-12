# -*- coding: utf-8 -*-
# flake8: noqa
from qiniu import Auth, put_file, etag,put_data
import qiniu.config
#需要填写你的 Access Key 和 Secret Key
access_key = 'c32Rbt3MXAB9qpAWm349D0ikyLdWCX_8nSD_LLBt'
secret_key = 'HtHGLLAlYyvyrQQYNnpy9-5HQzqxqVatgAxRcTZP'

def storage(file_data):
    """
    上传文件到七牛
    参数：file_data：上传的文件数据
    :return:
    """
    #构建鉴权对象
    q = Auth(access_key, secret_key)
    #要上传的空间
    bucket_name = 'ihonm-python'
    #上传后保存的文件名
    # key = 'my-python-logo.png'
    #生成上传 Token，可以指定过期时间等
    token = q.upload_token(bucket_name, None, 3600)

    #要上传文件的本地路径
    localfile = './sync/bbb.jpg'

    # 这个方法就是把文件保存到犀牛当中
    # 这里用put_data
    # ret, info = put_file(token, None, localfile)

    ret,info=put_data(token,None,file_data)

    print(info)  #_ResponseInfo__response:<Response [200]>, exception:None, status_code:200, text_body:{"hash":"FnwTip0klQtxFrvpX1vlWA8Qh9FC","key":"FnwTip0klQtxFrvpX1vlWA8Qh9FC"}, req_id:qRgAAADb_MmB2KEV, x_log:X-Log

    print(ret)  #{'hash': 'FnwTip0klQtxFrvpX1vlWA8Qh9FC', 'key': 'FnwTip0klQtxFrvpX1vlWA8Qh9FC'}
    if info.status_code==200:
        #表示上传成功，返回文件名
        return ret.get("key")
    else:
        #上传失败,以异常的方式来通知
        raise Exception("上传七牛失败")

    # assert ret['key'] == None
    # assert ret['hash'] == etag(localfile)


if __name__ == '__main__':
    # rb只能读，以二进制方式，wb是写，有的话清空再打开，没有的话创建一个
    with open("./ceshi.jpg","rb") as f:
        data=f.read()
    storage(data)