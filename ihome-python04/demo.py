import functools

def login_required(func):

    # 他的作用就是把下面改的__name__还原为曾经的
    @functools.wraps(func)
    def wrapper(*args,**kwargs):
        pass

    return wrapper


@login_required
def itcast():
    '''itcast python'''
    pass


#doc是注释内容
#没加装饰器以后 itcast    itcast python
# 加了装饰器以后wrapper.__name__    wrapper.__doc__  value：wrapper，None
print(itcast.__name__,itcast.__doc__)