from timeit import default_timer as timer

def giga_flop():
    x = 3.14159
    i = 0
    for i in range(500000000):
        x += 5.12313123
        x *= 0.5398394834
    return x

start = timer()
ret = giga_flop()
end = timer()
t = (end - start)*1000
print("Ans: %f" % ret)
print("Time: %.1f" % t)
