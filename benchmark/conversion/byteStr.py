import time
import random
import string

"""
Test conversion Str2Byte
    Test for 10 chars: 0 ms // gen 0 ms
    Test for 100 chars: 0 ms // gen 0 ms
    Test for 1000 chars: 0 ms // gen 1 ms
    Test for 10000 chars: 0 ms // gen 8 ms
    Test for 100000 chars: 0 ms // gen 83 ms
    Test for 1000000 chars: 1 ms // gen 784 ms
    Test for 10000000 chars: 7 ms // gen 7864 ms
    Test for 100000000 chars: 60 ms // gen 77105 ms
Test conversion Byte2Str
    Test for 10 chars: 7 ms // gen 1 ms
    Test for 100 chars: 0 ms // gen 0 ms
    Test for 1000 chars: 0 ms // gen 1 ms
    Test for 10000 chars: 0 ms // gen 7 ms
    Test for 100000 chars: 1 ms // gen 75 ms
    Test for 1000000 chars: 0 ms // gen 725 ms
    Test for 10000000 chars: 2 ms // gen 7354 ms
    Test for 100000000 chars: 53 ms // gen 71675 ms
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

ENCODING = 'utf-8'
if __name__ == '__main__':
    print("Test conversion Str2Byte")
    for p in range(1,9):
        n = pow(10,p)
        s, pt = generateString(n)
        t1 = getMs()
        b = s.encode(ENCODING)
        t2 = getMs()
        print(f'    Test for {n} chars: {t2-t1} ms // gen {pt} ms')

    print("Test conversion Byte2Str")
    for p in range(1,9):
        n = pow(10,p)
        b, pt = generateByte(n)
        t1 = getMs()
        s = b.decode(ENCODING)
        t2 = getMs()
        print(f'    Test for {n} chars: {t2-t1} ms // gen {pt} ms')

