import unittest
tc = unittest.TestCase()

class TestClass():
    def getFunction(self):
        def pow(a):
            return a*a
        def sqSum(a):
            return sum(pow(i) for i in range(1, a+1))
        return sqSum

    def testObj(self, obj):
        tc.assertEqual(obj(4), 30)