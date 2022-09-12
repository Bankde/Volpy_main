import unittest
tc = unittest.TestCase()

class TestClass():
    def getFunction(self):
        def recursive(a):
            if a == 0: return 0
            return a + recursive(a-1)
        return recursive

    def testObj(self, obj):
        tc.assertEqual(obj(5), 15)

class TestClass2():
    def getFunction(self):
        def recursiveTwo(a):
            if a == 0: return 0
            return a + recursiveOne(a-1)
        def recursiveOne(a):
            if a == 0: return 0
            return a * recursiveTwo(a-1)
        return recursiveOne

    def testObj(self, obj):
        tc.assertEqual(obj(6), 150)