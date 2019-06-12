
import random
a=""
for i in range(6):
    sms_code="%s"%random.randint(0,9)
    print(sms_code)
    print(type(sms_code))
    a=a+sms_code

print(a)