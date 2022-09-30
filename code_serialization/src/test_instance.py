import unittest
tc = unittest.TestCase()

class TestClass():
    def getFunction(self):
        class MyClass():
            def it_work(self):
                return 123
        return MyClass()

    def testObj(self, obj):
        tc.assertEqual(obj.it_work(), 123)