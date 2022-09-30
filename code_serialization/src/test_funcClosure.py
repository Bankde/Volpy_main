import unittest
tc = unittest.TestCase()

class TestClass():
    def getFunction(self):
        """
        my_add is pickled as source code of func_add_with
        """
        def func_add_with(c):
            def my_add(a):
                return a+c
            return my_add

        return func_add_with

    def testObj(self, obj):
        f = obj(4)
        tc.assertEqual(f(11), 15)

class TestClass2():
    def getFunction(self):
        """
        Inner function with closure (LOAD_DEREF) is considered local vars
        """
        def func_add_with(c):
            def my_add(a):
                return a+c
            return my_add

        return func_add_with(4)

    def testObj(self, obj):
        tc.assertEqual(obj(11), 15)