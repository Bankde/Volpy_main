import unittest
tc = unittest.TestCase()

'''
Fail lambda
1. From unable to get clean source code from lambda
2. No reference name to return after exec
    Use eval instead of exec can solve but we will need to add more
    feature to detect whether to use eval or exec.
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

class TestClass4():
    def getFunction(self):
        x = \
            lambda a: a + 10
        return x

    def testObj(self, obj):
        tc.assertEqual(obj(3), 13)