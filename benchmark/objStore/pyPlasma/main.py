from multiprocessing import Pool
import numpy as np
import pyarrow as pa
import pyarrow.plasma as plasma
import subprocess
from timeit import default_timer as timer
import os

client = None
object_store_size = 2 * 10 ** 9  # 2 GB
array_size = int(os.getenv("SIZE", 100000000))

# Connect to clients
def connect():
    global client
    client = plasma.connect('/tmp/store')
    np.random.seed(13)

def getLastIndex(arr_id):
    arr = client.get(arr_id)
    return arr[0]

def test():
    # Start the plasma store.
    p = subprocess.Popen(['plasma_store',
                          '-s', '/tmp/store',
                          '-m', str(object_store_size)])

    # Connect to the plasma store.
    connect()

    # Connect the processes in the pool.
    pool = Pool(initializer=connect, initargs=(), processes=1)

    # We use int64 here so it's fair comparison with javascript BigInt
    arr = np.random.randint(1000000, size=array_size, dtype=np.int64)

    # Time to store object / load and execute
    t1 = timer()
    arr_id = client.put(arr)
    s1 = pool.map(getLastIndex, [arr_id])[0]
    t2 = timer()

    s2 = arr[0]
    assert(s1 == s2)
    print('Time taken {} ms'.format((t2-t1)*1000))

    p.kill()

if __name__ == '__main__':
    test()