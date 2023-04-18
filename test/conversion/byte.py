import cloudpickle

def test(a):
    return a+1

s1 = cloudpickle.dumps(test)
print(f's1 type: ${type(s1)}')
v1 = memoryview(s1)
print(f'v1 type: ${type(v1)}')
f1 = cloudpickle.loads(v1)
print(f'f1 type: ${type(f1)}')
# Test
print(f1(4))
