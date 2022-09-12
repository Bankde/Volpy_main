import unittest
tc = unittest.TestCase()

class TestClass():
    def getFunction(self):
        global c
        c = 10
        def sumConst(a):
            return a + c
        return sumConst

    def testObj(self, obj):
        tc.assertEqual(obj(3), 13)