from timeit import default_timer as timer

def giga_flop():
    x = 3.14159
    i = 0
    for i in range(500000000):
        x += 5.12313123
        x *= 0.5398394834
    return x

with open("result.txt", "w") as f:
    for i in range(100):
        start = timer()
        ret = giga_flop()
        end = timer()
        t = (end - start)*1000
        # print("Ans: %.3f" % ret)
        print("Time: %.3f" % t)
        f.write("%.3f\n" % t)