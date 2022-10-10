import codepickle
import unittest
from timeit import default_timer as timer
import json

REPEAT = 100
LOOP = 1000
TESTSUITE = "without_module"

class SimpleModuleTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            with open("result.json", "r") as f:
                cls.test_data = json.load(f)
        except:
            cls.test_data = {}
        cls.data = {}
        codepickle.set_config_get_import(False)

    @classmethod
    def tearDownClass(cls):
        cls.test_data[TESTSUITE] = cls.data
        with open("result.json", "w+") as f:
            f.write(json.dumps(cls.test_data))

    def benchmarkDump(self, obj):
        testname = self._testMethodName
        speed = []
        for i in range(REPEAT):
            start = timer()
            for j in range(LOOP):
                pickled = codepickle.dumps(obj)
            end = timer()
            time_taken = round(end-start, 3)
            speed.append(time_taken)
        size = len(str(pickled))
        self.data[testname] = {
            "speed": speed,
            "size": size
        }
        return pickled

    def test_simple(self):
        import numpy
        const = 100
        def array_const(size):
            return numpy.zeros(size) + const

        pickled = self.benchmarkDump(array_const)

    def test_alias(self):
        import numpy as np
        const = 100
        def array_const(size):
            return np.zeros(size) + const

        pickled = self.benchmarkDump(array_const)

    def test_unused(self):
        import numpy as np
        import pandas
        const = 100
        def array_const(size):
            return np.zeros(size) + const

        pickled = self.benchmarkDump(array_const)

    def test_sub_simple(self):
        import numpy.random
        const = 1
        def randomIntPlusOne(maxInt):
            numpy.random.seed(0)
            return numpy.random.randint(maxInt) + const

        pickled = self.benchmarkDump(randomIntPlusOne)

    def test_sub_alias(self):
        import numpy.random as random
        const = 1
        def randomIntPlusOne(maxInt):
            random.seed(0)
            return random.randint(maxInt) + const

        pickled = self.benchmarkDump(randomIntPlusOne)

    def test_sub_duplicate(self):
        import numpy.random as random
        import numpy.fft as fft
        const = 1
        def testRandom(size):
            random.seed(0)
            return fft.fft(random.randint(0,2, size=4)) + const

        pickled = self.benchmarkDump(testRandom)

if __name__ == '__main__':
    unittest.main()