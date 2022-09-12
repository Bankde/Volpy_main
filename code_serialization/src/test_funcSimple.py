import unittest
tc = unittest.TestCase()

class TestClass():
    def getFunction(self):
        def sum(a, b):
            return a+b
        return sum

    def testObj(self, obj):
        tc.assertEqual(obj(17,18), 35)

class TestClass2():
    def getFunction(self):
        def sum(a, b=5):
            return a+b
        return sum

    def testObj(self, obj):
        tc.assertEqual(obj(17), 22)