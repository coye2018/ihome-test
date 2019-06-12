
li1=[1,2,3,4]
li2=[2,3,4,5]

def add(num1,num2):
    return num1+num2
def add_self(num):
    return num+2
ret=map(add,li1,li2)
print(ret)
print(list(ret))


ret2=map(add_self,li1)
print(ret2)
# 光打印是内存地址，需要转换成列表
print(list(ret2))
