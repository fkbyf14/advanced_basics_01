import json

from collections import Counter
from functools import reduce
from fractions import Fraction

count_ = 100
mis = 51
porog = mis / count_
if porog > 0.5:
    print(True, porog)
else:
    print(False, porog)
set_ = set('hellog')
frse = frozenset('jaa')
list_ = []
#if list_:
 #   print("reeeeeeeeeeeeeeeeetttttttttttttttwwwwwww")
c = Counter(list_)
count = c[5]
#print(c, count, list_, len(list_))

str_ = b'1.196.116.32 -  - [29/Jun/2017:03:50:22 +0300] "GET /api/v2/banner/25019354 HTTP/1.1" 200 927 "-" "Lynx/2.8.8dev.9 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/2.10.5" "-" "1498697422-2190034393-4708-9752759" "dc7161be3" 0.390\n'
chstr_ = str_.decode('utf-8')
print(type(chstr_))






