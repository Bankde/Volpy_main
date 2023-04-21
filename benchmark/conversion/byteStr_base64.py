import time
import random
import string
import base64

"""
Test conversion Str2Byte
    Test for 10 chars: 0 ms
    Test for 100 chars: 0 ms
    Test for 1000 chars: 0 ms
    Test for 10000 chars: 0 ms
    Test for 100000 chars: 1 ms
    Test for 1000000 chars: 3 ms
    Test for 10000000 chars: 29 ms
    Test for 100000000 chars: 299 ms
Test conversion Byte2Str
    Test for 10 chars: 0 ms
    Test for 100 chars: 0 ms
    Test for 1000 chars: 0 ms
    Test for 10000 chars: 0 ms
    Test for 100000 chars: 0 ms
    Test for 1000000 chars: 3 ms
    Test for 10000000 chars: 28 ms
    Test for 100000000 chars: 272 ms

gcloud
Test conversion Str2Byte
    Test for 10 chars: 0 ms
    Test for 100 chars: 0 ms
    Test for 1000 chars: 0 ms
    Test for 10000 chars: 0 ms
    Test for 100000 chars: 1 ms
    Test for 1000000 chars: 3 ms
    Test for 10000000 chars: 26 ms
    Test for 100000000 chars: 256 ms
Test conversion Byte2Str
    Test for 10 chars: 0 ms
    Test for 100 chars: 0 ms
    Test for 1000 chars: 0 ms
    Test for 10000 chars: 0 ms
    Test for 100000 chars: 0 ms
    Test for 1000000 chars: 1 ms
    Test for 10000000 chars: 18 ms
    Test for 100000000 chars: 180 ms
"""

def getMs():
    return round(time.time()*1000)

def generateString(n):
    t1 = getMs()
    s = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(n))
    t2 = getMs()
    return s, (t2-t1)

def generateByte(n):
    t1 = getMs()
    b = bytes([random.randrange(0,127) for _ in range(0,n)])
    t2 = getMs()
    return b, (t2-t1)

if __name__ == '__main__':
    time_s2b = []
    time_b2s = []
    gen = []
    for p in range(1,9):
        n = pow(10,p)
        b, pt = generateByte(n)
        t1 = getMs()
        s = base64.b64encode(b)
        t2 = getMs()
        b = base64.b64decode(s)
        t3 = getMs()
        time_b2s.append((t2-t1))
        time_s2b.append((t3-t2))
    
    print("Test conversion Str2Byte")
    for i, t in enumerate(time_s2b):
        n = pow(10,i+1)
        print(f'    Test for {n} chars: {t} ms')
    
    print("Test conversion Byte2Str")
    for i, t in enumerate(time_b2s):
        n = pow(10,i+1)
        print(f'    Test for {n} chars: {t} ms')

