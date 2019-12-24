import random

n = 0
bstr = ''
div = 32
d = {}
after_bstr = ''
for z in range(2**18,2**17,-1):
    n = z
    bstr = ''
    for i in range(4):
        tmp = ''
        rem = n % div
        if rem >= div // 2 :
            tmp = '2'
        elif rem >  div // 4 :
            tmp = '1'
        else:
            tmp = '0'
        bstr = bstr + tmp + ':'
        
        print(f"Tmp: {tmp} Rem: {rem}")
        #bstr = bstr + str(rem) + ':'
        n = n // div
    #print(tmp)
    if bstr in d:
        d[bstr] = d[bstr] + 1
    else:
        d[bstr] = 1
    print(bstr)
f=5
