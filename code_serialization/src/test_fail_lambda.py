import unittest
tc = unittest.TestCase()

'''
Fail from unable to get clean source code from lambda
'''

class TestClass():
    def getFunction(self):
        return lambda a: a + 10

    def testObj(self, obj):
        tc.assertEqual(obj(3), 13)

class TestClass2():
    def getFunction(self):
        return lambda a, b: a + b

    def testObj(self, obj):
        tc.assertEqual(obj(17,19), 36)

class TestClass3():
    def getFunction(self):
        c = 15
        return lambda a, b: a + b + c

    def testObj(self, obj):
        tc.assertEqual(obj(21,22), 58)