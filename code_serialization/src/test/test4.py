# Test recursive function

import codepickle

# def recursive(a):
#     if a == 0: return 0
#     return a + recursive(a-1)

# p = codepickle.dumps(recursive)
# f1 = codepickle.loads(p)
# # print(p)
# print(f1)
# print(f1(5))
# assert(f1(5) == 15)
# pass

def recursiveTwo(a):
    if a == 0: return 0
    return a + recursiveOne(a-1)
def recursiveOne(a):
    if a == 0: return 0
    return a * recursiveTwo(a-1)

p = codepickle.dumps(recursiveOne)
f1 = codepickle.loads(p)
# print(p)
print(f1)
print(f1(6))
assert(f1(6) == 150)
pass