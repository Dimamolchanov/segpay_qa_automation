import random
from math import log, ceil, floor


def randString(length=16):
    # put your letters in the following string
    your_letters = '01'
    return ''.join((random.choice(your_letters) for i in range(length)))

def binary(b, n):
    if b == '1':
        n = n * 2 + 1
    else:
        n = n * 2
    return n  #

# current base number ( 32,64,128....)
def cur_base(number):
    number = len(bin(number)[2:])
    return number

# upper limit of the base integer
def cur_base_decimal_upperlimit(number):
    number = 2 ** len(bin(number)[2:])
    return number

def from_dec_to_bin(number):
    processing_binary_string = format(number, 'b')
    # b_str= bin(rem)[2:].zfill(3)
    return processing_binary_string

# calculating lower base like 16,32,128
def base_floor_base(number):
    number = len(bin(number)[2:]) - 1
    return number

def base_floor_integer(number):
    lb = base_floor_base(number)
    number = 2 ** lb
    return number

def nn_binary_string(bin_str):
    b = bin_str[0:1]
    bin_str = bin_str[1:]
    return b, bin_str

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

def find_range(number):
    for i in range(10):
        number = number * 2 + 1
    number = number // 140
    return number

def Average(lst):
    return sum(lst) / len(lst)

def filler(d, number):
    top_base_integer = 2 ** cur_base(n)
    my_insert = 0
    for i in d:
        addon = d[i]
        if number + addon < top_base_integer:
            number = number + addon
            my_insert = addon
            break
    
    if d[1] == my_insert or d[2] == my_insert:
        for i in d:
            d[i] = d[i] * 2
    elif d[3] == my_insert or d[4] == my_insert:
        for i in d:
            d[i] = d[i] + 4
    
    elif d[5] == my_insert or d[6] == my_insert:
        for i in d:
            d[i] = d[i] - 4
    elif d[7] == my_insert or d[8] == my_insert:
        for i in d:
            d[i] = d[i] // 2
    
    # if array[0] == my_insert or array[1] == my_insert:
    #     for i in range(0, 7):
    #         array[i] = array[i] * 2
    # elif array[6] == my_insert or array[7] == my_insert:
    #     for i in range(0, 7):
    #         if i == 7:
    #             print (i)
    #         array[i] = array[i] //  2
    #         z=4
    # elif array[2] == my_insert or array[3] == my_insert:
    #     for i in range(0, 7):
    #         array[i] = array[i] + 4
    # elif array[4] == my_insert or array[5] == my_insert:
    #     for i in range(0, 7):
    #         array[i] = array[i] - 4
    # elif array[2] in my_insert or array[3] in my_insert or array[4] in my_insert or array[5] in my_insert:
    #     for i in range(0, 7):
    #         array[i] = array[i] + 1
    print(d)

def closest_power(x):
    possible_results = floor(log(x, 2)), ceil(log(x, 2))
    return min(possible_results, key= lambda z: abs(x-2**z))

d = {}

base = 15

#n = random.randint(2** 15,2** 16)
for i in range(2 ** base , 2 ** (base + 1)):
    
    
    rstr = ''
    n = i
    #n = 63000
   # print(cur_base(n))
    n = (n + 2 ** base) // 2 - 2 ** base
    curb = cur_base(n)
    #print(f"N: {n}  Curb: {curb}")
    while n > 32:
        n = n * 2
        curb = cur_base(n) - 1
        n = (n + 2 ** curb) // 2 - 2 ** curb
        rstr = rstr + str(curb) + ':'
       # print(f"        N: {n}  Curb: {curb}")
        
        
    
    
    
    
    
    if not rstr in d:
        d[rstr] = 1
    else:
        d[rstr] = d[rstr] + 1

z = 3










addon = 2** 32 // 32
cb = cur_base(addon)
d = {}
cnt = 0
deduction = 2** 28
n = 2 ** 32 #+ 2** cb
str_output = ''
nn = random.randint(2** 32,2** 33)
str_run = format(nn, 'b')
for b in str_run:
    nn = n
    n = binary(b,n)
    if n % 2 == 0 :
        n = n // 2
        str_output = str_output + '0'
    else:
        n = (n-1) // 2
        str_output = str_output + '1'
    n = n - deduction
    cnt += 1
    curb = cur_base(n)
    print(f"OriginN: {nn}  ModifiedN: {n}  Cnt: {cnt} Cbase: {curb}   ")
    z=3
    
    











str_base = ''
for i in range(2 ** 15 + 1, 2 ** 16):
    n = i
    cnt = 0
    str_base = ''
    current_base_ostatok = 40
    while current_base_ostatok > 4:
        origin_base = cur_base(n)
        
        distance_origin_n_upperlimit = 2 ** (origin_base) - n
        base_to_add = cur_base(distance_origin_n_upperlimit) - 1
        new_base = (2 ** origin_base) + 2 ** base_to_add
        new_n_addon = (new_base - n) // 2
        n = n + new_n_addon
        ostatok_do_upperlimit = 2 ** origin_base - n
        current_base_ostatok = cur_base(ostatok_do_upperlimit)
        # print(f"N: {n} Nbase: {origin_base}  Cnt: {cnt}   OstatokBase: {current_base_ostatok}")
        if cnt < 4:
            str_base = str_base + str(base_to_add) + ':'
        # if origin_base - current_base == 0:
        #     break
        n *= 2
        cnt += 1
    if not str_base in d:
        d[str_base] = 1
    else:
        d[str_base] = d[str_base] + 1
print(str_base)

#
        # while n > 2:
        #     n = n // 3
        #     if n % 3 == 0:
        #         str1 = str1 + '1'
        #     else:
        #         str1 = str1 + '0'
        # if not str1 in d:
        #     d[str1] = 1
        # else:
        #     d[str1] = d[str1] + 1






for i in range(2**10 + 1 ,2**11):
    n = i
    if n % 3 == 0:
        while n > 2:
            n = n // 2
            tmp = cur_base(n)
            if tmp == 4:
                if not n in d:
                    d[n] = 1
                else:
                    d[n] = d[n] + 1
        
z=3




n = random.randint(2** 32,2** 33)
print(n)
# rnd_str = format(rnd_n, 'b')
str_base = '001111111'
d = {}
cnt = 0
# for i in range(2**15 + 1 ,2**16):
tmp = cur_base(n)
while n > 10:
    rem = n % 8
    n = n // 8
    n = n - 100000000
    tmp_str = format(rem, 'b').rjust(3,'0')
    for b in tmp_str:
        n = binary(b,n)
    tmp1 = cur_base(n)
    cnt += 1
    z=4
    
z=4







origin_base = cur_base(n)
n = ((2 ** origin_base) - n ) // 2 + n
print(n)
# 382
base = 2 **  (origin_base - 1)
base = base + base // 2
n =  n - (n - base) // 2
print(n)
n = ((2 ** origin_base - 32 ) - n ) // 2 + n
print(n)






z=3
































pair = [4,5]

n = 301
cnt = 0
while n > 9:
    rem = n % 9
    if rem in pair:
        rem = 5
        n = n * 2 + 1
    n = n // 9
    rem_str = format(rem, 'b').rjust(3, '0')
    for b in rem_str:
        n = binary(b, n)

    cnt +=1
print(f"Cnt: {cnt} FinalN: {n}")
z=3





for i in range(2**8,2**9):
    n = i
    rem = n % 9

    if rem in pair:
        rem = 3
        n = n * 2
    n = n // 9
    rem_str = format(rem, 'b').rjust(3, '0')
    for b in rem_str:
        n = binary(b,n)
        
        
        
        
        
        
        print(f"Rem: {rem}")
        n = n // 5
        print(f"ModifiedN: {n}")

        n = n * 5
        while n % 9 not in pair:
            n = n +1
        print(f"OriginN: {i}   Target: {n}")
    if n != i:
        print(f"Missmatch - Original: {i}   Got: {n}")

        z=4



d = {}
d10 = {}
ostatok = 8
#n = random.randint(2**15,2**16)

for i in range(2 ** 15 + 1, 2 ** 16):
    cnt = 0
    str_rem = ''
    str_01 = ''
    n = i
    while n > 1:
        rem = n % 9
        n = n // 9
        str_rem = str_rem + str(rem) + ':'
        if rem == ostatok:
            str_01 = str_01 + '1'
        else:
            str_01 = str_01 + '0'
        
        
        
        
        
    if not str_rem in d:
        d[str_rem] = 1
    else:
        d[str_rem] = d[str_rem] + 1

    if not str_01 in d10:
        d10[str_01] = 1
    else:
        d10[str_01] = d10[str_01] + 1
    z=3
# x = {k: v for k, v in sorted(d10.items(), key=lambda item: item[1])}
# y = dict(sorted(d10.items(), key=lambda item: item[1]))


sorted_values = sorted(d10.values()) # Sort the values
sorted_dict = {}

for i in sorted_values:
    for k in d10.keys():
        if d10[k] == i:
            sorted_dict[k] = d10[k]
            break

print(sorted_dict)


z=4




for i in range(2**15+1,2**16):
    cnt = 0
    str_base = ''
    n = i
    while cur_base(n) > 6:
        origin_base = cur_base(n)
        cnt +=1
        blimit = 2 ** (cur_base(n)-1)
        n = distance_origin_n_upperlimit =blimit -( n - blimit)
        #n = distance_origin_n_upperlimit = 2 ** cur_base(n) - n
        current_base = tmp = cur_base(n)
        print(f"N: {n} Nbase: {current_base}  Cnt: {cnt}   DiffInBases: {origin_base - current_base}")
        str_base = str_base + str(origin_base - current_base) + ':'
        if origin_base - current_base == 0:
            break
        
    if not str_base in d:
        d[str_base] = 1
    else:
        d[str_base] =  d[str_base] + 1
    print(str_base)
z=3




#
#
# print(f"OriginN: {n}  Dist: {distance_origin_n_upperlimit}")
# current_base = tmp = cur_base(n)  # find base single digit , 8,10,64
# extra_ontopof_base = 2 ** current_base + 2 ** extra_value
# half_distance_from_extra_to_n = (extra_ontopof_base - n) // 2  # half distance between current n and extra value
# n = n + half_distance_from_extra_to_n
# distance_from_upper_limit = 2 ** current_base - n
# if cur_base(n) > tmp:





n = 1055
pair = [16,18,17]
while n > 18:
    nn = n
    rem = n % 18
    if rem in pair:
        print(f"CurRem: {rem}")
        rem = 2
    n = n // 18
    rem_str = format(rem, 'b').rjust(4,'0')
    for b in rem_str:
        n = binary(b,n)
        
    print(f"OriginN: {nn} ModifN: {n}   Rem: {rem} Diff: {nn - n}")
    z=4








#-----------------------------------------------------------------------------
cnt = 0
extra_value = 55 # add extra value on top of the upper limit of current base
n_convert_bin = random.randint(2 **  63,2 ** 64)
running_str = format(n_convert_bin, 'b') # convert to binary
#n = random.randint(2**32, 2** 33)
n = random.randint(2 **  63,2 ** 64) # 650000
origin = n


for b in running_str:
    cnt += 1
    distance_origin_n_upperlimit = 2 ** cur_base(n) - n
    print(f"OriginN: {n}  Dist: {distance_origin_n_upperlimit}")
    current_base = tmp  = cur_base(n)  # find base single digit , 8,10,64
    extra_ontopof_base = 2 ** current_base + 2 ** extra_value
    half_distance_from_extra_to_n = (extra_ontopof_base - n ) // 2 # half distance between current n and extra value
    n = n + half_distance_from_extra_to_n
    distance_from_upper_limit = 2 ** current_base - n
    if cur_base(n) > tmp:
        print('crosslimit')
    print(f"AboveLimit: {extra_ontopof_base}  HalfDistn: {half_distance_from_extra_to_n}  CurrentN: {n} DistUpper{distance_from_upper_limit}  Cnt: {cnt}")
    #extra_value = extra_value * 2
    n = binary(b, n)
    #print(n)
    z=3
    
final_dist = 100

while final_dist > 5:
    cnt +=1
    print(f"OriginN:{n}")
    tmp = cur_base_decimal_upperlimit(n) - n
    print(f"DistancetoUpperLimit:{tmp}")
    p2 = closest_power(tmp)
    print(p2)
    
    dist_base = cur_base(tmp)
    print(f"BaseofDistancetoUpperLimit:{dist_base}")
    above_base = cur_base_decimal_upperlimit(n) + 2 ** (dist_base - 1)
    print(f"SummaryAboveLimit: {above_base}")
    n = add_distance_to_n = (above_base - n) // 2 + n
    print(f"AddHalfDistance_to_N:{add_distance_to_n}")
    final_dist = cur_base_decimal_upperlimit(n) - n
    print(f"LeftDistance_toN:{final_dist}")
    base_final_dist = cur_base(final_dist)
    print(f"final_dist_Base: {base_final_dist}")
print(cnt)
z=4

for i in range(16):
    st = format(i, 'b').rjust(5, '0')
    if not '11' in st:
        print(st)
        cnt +=1


#####################################################################
# array = [50, 35, 26,18 , 13, 7, 4, 2]
# array = [2, 4, 6, 8, 11, 15, 19, 22]
d = {}
d[1] = 50
d[2] = 35
d[3] = 26
d[4] = 18
d[5] = 13
d[6] = 7
d[7] = 4
d[8] = 2
# n = 13
# tmp = filler(d,n)
cnt = 0
cnt_up = 0
n = nn = random.randint(2 ** 15, 2 ** 16)
print(n)

rem = n % 100
print(f"Rem: {rem}")
tmp = n = n // 100
while n % 100 != rem:
    cnt += 1
    n = n - 1
print(f"Cnt:{cnt}   Rem: {n % 100}")
print(n)
print(f"Distance: {(tmp * 1000) - (n * 1000)}")
z = 4
n = n * 100
n = n + rem
while n != nn:
    cnt_up += 1
    n = n + 100
print(f"N: {n}   CntDistance: {cnt}")

rem_compare = 3
d = {}
lst = []
cnt = 0
n = random.randint(2 ** 8, 2 ** 9)
# n = 290
bstr = from_dec_to_bin(n)  # convert integer to binary
print(bstr)
div = 8;
cnt_addons = 0
n = 0

for b in bstr:
    cnt += 1
    n = binary(b, n)
    if cnt % 4 == 0:  # get the base, identify lower base, divide by div= 9
        cnt_addons = 0
        top_base_integer = 2 ** cur_base(n)

for b in bstr:
    cnt += 1
    n = binary(b, n)
    if cnt % 4 == 0:  # get the base, identify lower base, divide by div= 9
        cnt_addons = 0
        top_base_integer = 2 ** cur_base(n)
        lb_int = base_floor_integer(n)  # base floor as integer ,32,64,128
        addon = lb_int // div
        while (n + addon) < top_base_integer:
            cnt_addons += 1
            n = n + addon
        print(f"CurN: {n}    AddonSize: {addon}  CntAddons: {cnt_addons}  DistanceFromTopInt: {top_base_integer - n} DistFromTopBase: {cur_base(top_base_integer - n)}")
        
        z = 4

z = 4
#
#
#
#
# div = 32
# n = 0
# for b in bstr:
#     cnt +=1
#     n = bin_calc(n,b)
#
#     if cnt > 6:
#         cbase = cur_base_base(n)
#         addon = (2 ** (cbase-1))  // div
#         n = n + addon
#         distance = (2** cbase) - n
#         distance_base = cur_base_base(distance)
#         print(f"Cnt: {cnt}    CurAddon: {addon}  Cbase: {cbase}  Distance: {distance}  DistanceBase: {distance_base}")
#         if distance == 0:
#             break
#
#         z=3
#
#
#
#
# #j = n = random.randint(2 ** 31, 2 ** 32)
#
#
# for i in range(2**18, 2 ** 19):
#     n = i
#     tmp_str = ''
#     cnt = 0
#     while n > 16:
#         cnt +=1
#         cbase = cur_base_base(n)
#         nx = 2 ** (cbase - 1) // 9
#         while n + nx < 2** cbase:
#             n = n + nx
#
#         lbase = 2 ** (cbase - 1)
#         tmp = n - lbase
#         n = lbase - tmp
#         diffbase = cur_base_base(n)
#         diff = cbase - diffbase
#         tmp_str = tmp_str + str(diff)
#         if diff == 0:
#             break
#         #print(f"N: {n}   Nbase:{diffbase}  ") #DiffBase: {tmp_str}
#         z=4
#     if not tmp_str in d:
#         d[tmp_str] = 1
#     else:
#         d[tmp_str] = d[tmp_str] + 1
#     #print(cnt)
#
#
#
# #bstr = (format(n, 'b'))
#
#
#
#
#
#
# for i in range(2**15, 2 ** 16):
#     if i % 3 == 0:
#         n = i
#         n = n // 154 * 256
#         diff = i - n
#         lst.append(diff)
#         ib = cur_base_base(i)
#         nb = cur_base_base(n)
#         if ib==nb:
#             cnt+=1
#         else:
#             cnt1 += 1
#
#
#
#
#         #print(f"Ibase: {cur_base_base(i)}    Nbase: {cur_base_base(n)}")
# print(f"Average: {int(Average(lst))}  Bsame: {cnt}   Bdiff: {cnt1}")
#
#
#
#
#
# for i in range(2**12, 2 ** 13):
#     if i % 3 == 0:
#         tstr = str(i)[:-1]
#         j = n = int(tstr)
#         tmp = ((n * 4) // 55) * 256
#
#         tmp1 = ((i // 3) // 55) * 4  * 256
#
#         tmp2 = i // 165 * 256 -512
#
#         #print(f"Original: {i}  Final: {tmp} Drop3: {n}  Div3: {i // 3}   Back: {n * 4}   Diff: {i-tmp}   DiffDiv3: {i-tmp1} OringId: {i - tmp2} ")
#
#         print(f"         Original: {i}  Final: {tmp2}   OringId: {i - tmp2} ")
#         z=4
#     else:
#         n = i
#         n = n // 300 * 256
#         print(f"Original: {i}  Final: {n}   Diffrence: {i - n} ")
#
#
#
#
#
#
# for i in range(2**15, 2 ** 16):
#     j = n = i
#     cnt = 0
#     rem = n % 100
#     x = n = n // 100
#     while n % 100 != rem:
#         n = n - 1
#
#     distance = j - (n*100)
#     cbase = cur_base_base(distance)
#    # print(f"Original: {j} DivN: {x}  CurrentN: {n}  Distance: {distance} DistanceBase: {cbase}")
#     #print(j - (n * 100))
#     while j - (n * 100) > 100:
#         cnt += 1
#         n += 2
#     print(j - (n * 100))
#
#     if not cnt in d:
#         d[cnt] = 1
#     else:
#         d[cnt] = d[cnt] + 1
#
#    # print(cnt)
#
#
#
#
#
# rem = n % 95
# print (f"N: {n}   Rem: {rem}")
# n = n // 2
#
# while n % 95  != rem :
#     n = n - 1
#     cnt +=1
#     print(f"N: {n}   Rem: {n % 95}  Cnt: {cnt}")
#
#
#     #print(f"N:{n * 2}     Rem: {(n * 2) % 95}  Diff: {rem - (n % 95)}")
#
#
# print (f"Orignal: {j}  Mod: {n}    Diff: {j - n}")
# cnt = 0
#
# while n > 50:
#     cnt += 1
#     r = ((n * 2) % 95 )
#     r1 = ((n * 2 + 1) % 95)
#     if r == rem:
#         print(f"N: {n}   Rem: {r}  Cnt: {cnt}")
#         break
#
#     if r1 == rem:
#         print(f"N: {n}   Rem: {r1}  Cnt: {cnt}")
#         break
#     n +=1
#     print(f"N:{n * 2}     Rem: {(n * 2) % 95}  Diff: {rem - (n % 95)}")
#
#
#
#
#
#
# z=4
#
#
#
#
#
#
#
#
#
#
#
# for i in range(2**8, 2 ** 9):
#     rem = i % 8
#
#     if rem > rem_compare and i % 22 > 8 and i % 80 < 8:
#         cnt +=1
#         print(f"Original Rem: {rem}  D12: {i % 12} | D18: {i % 18} | D22: {i % 22} | D30: {i % 30} | D48: {i % 48} | D65: {i % 65} | D80: {i % 80}")
#
#
#     # n = i
#     # while n < 2**9:
#     #     n = n +1
#     #     if n % 8 == rem:
#     #         print(f"Original Rem: {rem}  D12: {i % 12} | D18: {i % 18} | D22: {i % 22} | D30: {i % 30} | D48: {i % 48} | D65: {i % 65} | D80: {i % 80}")
#     #
#     #
#     # if rem > 3 :
#     #     print(f"Original Rem: {rem}  D12: {i % 12} | D18: {i % 18} | D22: {i % 22} | D30: {i % 30} | D48: {i % 48} | D65: {i % 65} | D80: {i % 80}")
#     #
#
#
#         # n = i
#         # while n < 2**16:
#         #     n +=1
#         #     rem1 = n % 90
#         #     if rem1 < (90 // 8):
#         #         print(f"N: {n} | DIstance: {n-i}")
#
#
#
#     #print(f"D8:{i % 8} | D12: {i % 12} | D18: {i % 18} | D22: {i % 22} | D30: {i % 30} | D48: {i % 48} | D65: {i % 65} | D80: {i % 80}")
#     z=4
# print(cnt)
#
#
#
#
#
#
#
#
#
#
# for i in range(2**7, 2 ** 8):
#     print(f"D8:{i % 8} | D12: {i % 12} | D18: {i % 18} | D22: {i % 22} | D30: {i % 30} | D48: {i % 48} | D65: {i % 65} | D80: {i % 80}")
#     z=4
#
#
#
#
#
#
