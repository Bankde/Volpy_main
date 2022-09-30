import unittest
tc = unittest.TestCase()

class TestClass():
    def getFunction(self):
        class MyClass():
            def it_work(self):
                return 123
        return MyClass

    def testObj(self, obj):
        inst = obj()
        tc.assertEqual(inst.it_work(), 123)