import random

def randString(length=16):
    # put your letters in the following string
    your_letters = '01'
    return ''.join((random.choice(your_letters) for i in range(length)))

def bin_calc(n, b):
    if b == '1':
        n = n * 2 + 1
    else:
        n = n * 2
    return n

def one_4(number):
    number = number // 2 // 4
    return number

def one_3(number):
    number = number // 2 // 3
    return number

def one_8(number):
    number = number // 2 // 8
    return number

def binary(b, n):
    if b == '1':
        n = n * 2 + 1
    else:
        n = n * 2
    return n

def cur_base_base(number):
    number = len(bin(number)[2:])
    return number

def cur_base_decimal(number):
    number = 2 ** len(bin(number)[2:])
    return number

def from_dec_to_bin(number):
    processing_binary_string = format(number, 'b')
    # b_str= bin(rem)[2:].zfill(3)
    return processing_binary_string

def base_floor(number):
    number = 2 ** len(bin(number)[2:])
    n_currentbase_dec = number // 2
    return n_currentbase_dec

def nn_binary_string(bin_str):
    b = bin_str[0:1]
    bin_str = bin_str[1:]
    return b, bin_str

def the_diff(number):
    floor = base_floor(number)
    top = cur_base_decimal(number)
    diff_to_floor = number - floor
    diff_to_top = top - number
    diff_to_floor_base = cur_base_base(diff_to_floor)
    diff_to_top_base = cur_base_base(diff_to_top)
    tmp_str = f"To_Floor:{diff_to_floor} | FloorDiff_Base: {diff_to_floor_base} | To_top: {diff_to_top} | TopDiff_Base: {diff_to_top_base}"
    return tmp_str

def analyze_n(number, running_string):
    switch_to_inside = 1
    n_currentbase_base = cur_base_base(n)
    n_currentbase_dec = cur_base_decimal(n)
    n_base_floor = base_floor(n)
    n_one_4th = one_4((n_currentbase_dec))
    n_one_8th = one_8(n_currentbase_dec)
    if number - n_one_4th > n_base_floor:
        number = number - n_one_4th
        running_string = running_string + '1'
    else:
        running_string = running_string + '0'
        number = number - n_base_floor
        switch_to_inside = 0
    return number, running_string, switch_to_inside

def analyze_n_3(number, running_string):
    switch_to_inside = 1
    n_currentbase_base = cur_base_base(n)
    n_currentbase_dec = cur_base_decimal(n)
    n_base_floor = base_floor(n)
    n_one_3th = one_3((n_currentbase_dec))
    
    if number - n_one_3th > n_base_floor:
        number = number - n_one_3th
        running_string = running_string + '1'
    else:
        running_string = running_string + '0'
        # number = number - n_base_floor
        switch_to_inside = 0
    return number, running_string, switch_to_inside

def move_down(number):
    current_base = len(bin(number)[2:])
    curent_floor = 2 ** (current_base - 1)
    tmp = number - curent_floor
    n = curent_floor - tmp
    return n

def n_to_base(number):
    current_base = len(bin(number)[2:])
    curent_floor = 2 ** (current_base - 1)
    tmp = (n - curent_floor) // 2 + curent_floor
    return tmp

def sum_digits3(n):
    r = 0
    while n:
        r, n = r + n % 10, n // 10
    return r

def sum_digits2(n):
    s = 0
    while n:
        n, remainder = divmod(n, 10)
        s += remainder
    return s
def get_even(numbers):
    even_nums = [num for num in numbers if not num % 2]
    return even_nums

#####################################################################

str1 = ''
d = {}
# print(bin(2032)[2:])

rs = 1
#n = random.randint(2 ** 11, 2 ** 12)
# n = 2966
##print(n)

for i in range(2 ** 9, 2 ** 10):
    n = i
    n = n * 2
    remp = n % 9
    n = n // 2
    rem1 = n % 9
    # n = n // 2
    # rem2 = n % 9
    nstr = f"{str(remp)}{str(rem1)}"
    #nstr = f"{str(remp)}{str(rem1)}{str(rem2)}"
    
    if nstr in d:
        d[nstr] = d[nstr] + 1
    else:
        d[nstr] = 1
    
    
    print(f"Remp: {remp}   Rem1: {rem1}  ")
    #print(f"Remp: {rem1}   Rem1: {rem1}   Rem2: {rem2}")
    
    
    
    
    
    
    
    # rem = n % 9
    # n = n * 2
    # rem2 = n % 9
    # print(f"Rem: {rem}     Rem2: {rem2}")
    
    


print(1052 % 9)
for i in range(1):
    nnn = 1058
    bstr = (format(nnn, 'b'))
    n = 0
    cnt = 0
    for b in bstr:
        cnt += 1
        if cnt == 8:
            n = n + 2
        n = bin_calc(n, b)
    rem = n % 9
    print(f" Rem: {rem}")



























while n > 18:
    cnt = 0
    origin = nn = n
    n8 = n = n * 8
    r = rem = n % 9
    while n % 9 != 0:
        cnt += 1
        n = n + 1
    n = n // 9
    if rem in d:
        d[rem] = d[rem] + 1
    else:
        d[rem] = 1
    print(f"Rem: {rem} Cnt: {cnt} PreviousN: {nn}  CurrentN: {n}  T8: {n8}  T9: {n * 9} ")
    
    # reverse
    nn = n
    rn9 = n = n * 9
    rem = n % 8
    cnt = 0
    while n % 8 != 0:
        n = n - 1
        cnt += 1
    
    if n == n8:
        print('        Match')
    else:
        print(f"                                                       Fail     Rem {r}")
    
    print(f"Rem8: {rem} Cnt: {cnt} PreviousN: {nn}  CurrentN: {n}  T8: {n8}  T9: {n * 9} ")
    n = nn

for i in range(8):
    bstr = (format(i, 'b')).rjust(3, '0')
    n = 35
    for b in bstr:
        n = bin_calc(n, b)
    print(n % 9)

for n in range(65536):
    if n % 2 == 0:
        rs = sum_digits2(n)
        
        while len(str(rs)) > 2:
            rs = sum_digits2(rs)
        
        print(rs)
        
        if rs in d:
            d[rs] = d[rs] + 1
        else:
            d[rs] = 1
    # print(f"{n % 9}   {n}  {n//9} {sum_digits2(n)}    ")

n = random.randint(2 ** 31, 2 ** 32)
# n = 4323
for i in range(32):
    odd = False
    n = n * 2
    nn = n
    rem = n % 3
    if (n - rem) % 2 != 0:
        odd = True
        str = str + 'B'
        n = n // 3
    elif n % 4 != 0:
        str = str + '1'
        n = n // 4
        if n % 2 != 0:
            str = str + 'X'
    elif n % 4 == 0:
        str = str + '0'
        n = n // 4
        if n % 2 != 0:
            str = str + 'X'
    else:
        print('oops')
    if n < 3: break
    print(f"Org:{nn}  N3:{n}")
    
    print(str)

for i in range(2 ** 15, 2 ** 16):
    n = i
    # n = 435443454
    while n > 9:
        nn = n
        cnt += 1
        rem = n % 3
        
        if rem == 2:
            n = n // 3
            rem2 = n % 100
            b_str = '0' + bin(rem)[2:].zfill(7)
            n = n // 100
        elif rem == 0:
            n = n // 3
            rem2 = n % 100
            b_str = '1' + bin(rem)[2:].zfill(7)
            n = n // 100
        else:
            n = m_n = int(str(n)[0:-1])  # n // 3 #
            
            print(f"N:{nn}  | ModifN:{m_n} ")
            
            rem2 = n % 55
            tmp = 200 + rem
            b_str = bin(tmp)[2:]  # + '1'
            n = n // 55
        
        for b in b_str:
            n = bin_calc(n, b)
        
        print(f"Cnt:{cnt} | Orig: {nn} | N:{n} | Rem: {rem} | Rem2:{rem2} | Bstr: {b_str}")
    
    str_compare = ''
    #
    # for j in range(5):
    #     str_compare  = str_compare + str(n %  9)
    #     n = n // 9
    # str_compare = str_compare[1:]
    # if  str_compare in d:
    #     cnt += 1
    #     d[str_compare] = d[str_compare] + 1
    #     print(str_compare)
    # else:
    #     d[str_compare] = 1

n = random.randint(2 ** 15, 2 ** 16)
print(n)
compare_str = str(n)[1:]

for i in range(2 ** 14, 2 ** 15):
    n = i
    str_compare = ''
    for j in range(4):
        str_compare = str_compare + str(n % 9)
        n = n // 9
    if str_compare == compare_str:
        print(i)
    
    b = 3

n = random.randint(2 ** 19, 2 ** 20)
print(n)
processing_binary_string = from_dec_to_bin(n)
for i in range(32):
    tmp = nn_binary_string(processing_binary_string)
    b = tmp[0]
    processing_binary_string = tmp[1]
    n = binary(b, n)
    n = n_to_base(n)
    n = n // 8
    n = move_down(n)
    n = n * 8
    print(n)
    z = 3

####################################################################


n = (2 ** 9 - 1)  # - (2**64 // 2 -1)
x = 2 ** 8 + (2 ** 8 // 2)
print(from_dec_to_bin(x))
n_64 = 2 ** 9 // 32
print(f"{from_dec_to_bin(n)}  N:{n} ")
for i in range(32):
    n = n - n_64
    print(f"{from_dec_to_bin(n)} |  N:{n} ")

cnt = 0
n = random.randint(2 ** 31, 2 ** 32)
running_string = ''
processing_binary_string = from_dec_to_bin(n)

n = 62  # random.randint(2 ** 6, 2 ** 7)
print((f"{from_dec_to_bin(n)}                 OriginalN: {n}"))
for b in processing_binary_string:
    cnt += 1
    current_floor = base_floor(n)
    cur_n = n
    tmp = analyze_n_3(n, running_string)
    n = tmp[0]
    running_string = tmp[1]
    switch_to_inside = tmp[2]
    n = bin_calc(n, b)
    processing_binary_string = from_dec_to_bin(n)
    differences = the_diff(n)
    print((f"{processing_binary_string}   | OriginalN: {cur_n} | NewN: {n}  | ProcessingString: {running_string}  Cnt:{cnt}  | {differences}"))
    g = 4

for q in processing_binary_string:
    cnt += 1
    current_floor = base_floor(n)
    cur_n = n
    tmp = analyze_n(n, running_string)
    n = tmp[0]
    running_string = tmp[1]
    switch_to_inside = tmp[2]
    if tmp[2] == 0:
        for i in range(2):
            res = nn_binary_string(processing_binary_string)
            n = bin_calc(n, res[0])
            processing_binary_string = res[1]
        n = current_floor + n
        cnt = cnt + 1
    else:
        res = nn_binary_string(processing_binary_string)
        n = bin_calc(n, res[0])
        processing_binary_string = res[1]
    processing_binary_string = from_dec_to_bin(n)
    differences = the_diff(n)
    print((f"{processing_binary_string}   | OriginalN: {cur_n} | NewN: {n}  | ProcessingString: {running_string}  Cnt:{cnt}  | {differences}"))
    g = 4

d = {}
cnt = 0

cnt_inside = 0
n = random.randint(2 ** 7, 2 ** 8)
n = 195
print(f"{format(n, 'b')}  N: {n}")
bstr = (format(random.randint(2 ** 32, 2 ** 33), 'b'))
addon = ''
switch_to_inside = 0
for b in bstr:
    cnt += 1
    nn = n
    current_base_dec = 2 ** (len(format(n, 'b')))
    current_base_floor = 2 ** (len(format(n, 'b')) - 1)
    one_4 = current_base_dec // 2 // 4
    one_8 = current_base_dec // 2 // 8
    
    if switch_to_inside == 1:
        cnt_inside = cnt_inside + 1
        if cnt_inside == 2:
            switch_to_inside == 0
        
        n = n - current_base_dec
        
        switch_to_inside = 1
    
    if n - one_4 > current_base_floor:
        n = n - one_4
        addon = 'One4'
    else:
        n = n - current_base_dec
        switch_to_inside = 1
        
        n = n + one_4
        addon = ' - One8'
    n = binary(b, n)
    bin_n = format(n, 'b')
    current_base_top = 2 ** (len(format(n, 'b')))
    dist = n - current_base_dec
    dist_base = 2 ** (len(format(dist, 'b')))
    
    print(
            f"{bin_n}    OringalN: {nn}  CurrentN: {n}     One4: {one_4}   One8: {one_8}   CurrentBase TOP: {current_base_top} |  Added: {addon} Distance: {dist_base}  Distance_to_Base: {dist}    Cnt: {cnt}")

nn = 2 ** 26 + (2 ** 26 // 2) + (2 ** 26 // 4)
top_base = 2 ** 27
for n in range(nn, top_base):
    s = format(n, 'b')
    bstr = format(s)[0:5]
    if bstr in d:
        d[bstr] = d[bstr] + 1
    else:
        d[bstr] = 1

# print(format(n, 'b'))


n = random.randint(2 ** 31, 2 ** 32)

l_base = 2 ** 31
top_base = 2 ** 32
div = 8
bstr = (format(random.randint(2 ** 31, 2 ** 32), 'b'))
# slice_cnt = 0
for b in bstr:
    print(f"{(format(n, 'b'))}    OriginalN : {n}")
    cnt = cnt + 1
    current_base_dec = 2 ** (len(format(n, 'b')))
    slice = current_base_dec // 2 // div
    slice_cnt = 0
    while n + slice < current_base_dec:
        n = n + slice
        slice_cnt = slice_cnt + 1
    div = div * 2
    bin_n = (format(n, 'b'))
    n = binary(b, n)
    
    print(f"{bin_n}     CurrentN: {n}     SLiceCnt: {slice_cnt}    Cnt: {cnt}")
    if bin_n[0:32] == '11111111111111111111111111111111':
        print(f"Cnt: {cnt}   Done")

z = 0

# n = random.randint(2**31,2**32)
# print(f"{(format(n, 'b'))}    OriginalN : {n}")
# l_base = 2 ** 31
# top_base = 2 ** 32
# for i in range(64):
#     tmp = (n - l_base) // 2
#     n = l_base + tmp
#     print(f"{(format(n, 'b'))}  ModifiedN: {n}")
#     z=0


bstr = 16 * '1' + 16 * '0'
dec = int(bstr, 2)
print(2 ** 32 - dec)
print(dec)
print(dec // 65536)
x = 2 ** 32 // 8
tmp = 2 ** 31 - x

print(format(tmp, 'b'))

n = random.randint(2 ** 15, 2 ** 16)
n2 = random.randint(2 ** 15, 2 ** 16)

bstr = (format(n2, 'b'))
cnt = 0

bin = (format(n, 'b'))
print(bin)
div = 8
origin_start = 4096
for b in bstr:
    cnt = cnt + 1
    currentbase = 2 ** (len(format(n, 'b')))
    one_8 = currentbase // div
    if n + one_8 < 2 ** (len(format(n, 'b'))):
        n = n + one_8
        tmp = (format(n, 'b'))
        print(f"{tmp}    N:{n}       Distance:{currentbase - n}   One_8: {one_8}     Cnt:{cnt}")
    else:
        currentbase = one_8
        print(f"N:{n}   Distance:{(2 ** (len(format(n, 'b')))) - n}   One_8: {one_8}     Cnt:{cnt}")
    n = binary(b, n)

for z in range(2 ** 18, 2 ** 19):
    n = z
    # n = 262144
    cnt = 0
    div = 512
    rem = 0
    # print(n % div)
    while n % div > 16:
        rem = n % div
        cnt += 1
        div = div + 5
    print(f"Rem: {n % div} | Div: {div} | Cnt: {cnt}")

after_bstr = ''
for z in range(2 ** 18, 2 ** 17, -1):
    n = z
    bstr = ''
    for i in range(4):
        tmp = ''
        rem = n % div
        if rem >= div // 2:
            tmp = '2'
        elif rem > div // 4:
            tmp = '1'
        else:
            tmp = '0'
        bstr = bstr + tmp + ':'
        
        print(f"Tmp: {tmp} Rem: {rem}")
        # bstr = bstr + str(rem) + ':'
        n = n // div
    # print(tmp)
    if bstr in d:
        d[bstr] = d[bstr] + 1
    else:
        d[bstr] = 1
    print(bstr)
f = 5
