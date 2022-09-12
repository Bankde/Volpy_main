import unittest
tc = unittest.TestCase()

class TestClass():
    def getFunction(self):
        def sumRandomSeed(a):
            import numpy
            numpy.random.seed(a)
            return numpy.sum(numpy.random.randint(0,10,100))
        return sumRandomSeed

    def testObj(self, obj):
        tc.assertEqual(obj(11), 415)

class TestClass2():
    def getFunction(self):
        import numpy as np
        def sumRandomSeed(a):
            np.random.seed(a)
            return np.sum(np.random.randint(0,10,100))
        return sumRandomSeed

    def testObj(self, obj):
        tc.assertEqual(obj(16), 431)

import numpy as np2
class TestClass3():
    def getFunction(self):
        def sumRandomSeed(a):
            np2.random.seed(a)
            return np2.sum(np2.random.randint(0,10,100))
        return sumRandomSeed

    def testObj(self, obj):
        tc.assertEqual(obj(16), 431)