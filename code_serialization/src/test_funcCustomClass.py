import unittest
tc = unittest.TestCase()

class TestClass():
    def getFunction(self):
        class Test():
            def __init__(self, b):
                self.a = 10
                self.b = b
            def sum(self):
                return self.a + self.b
        
        def sumConst(b):
            t = Test(b)
            return t.sum()

        return sumConst

    def testObj(self, obj):
        tc.assertEqual(obj(4), 14)