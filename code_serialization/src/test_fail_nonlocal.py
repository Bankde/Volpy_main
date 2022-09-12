import unittest
tc = unittest.TestCase()

'''
Fail of using non local
'''

a=5
b=3

class TestClass():
    def getFunction(self):
        def foo():
            a = 1
            def f1():
                nonlocal a
                a = a + b
                return a
            return f1
        def f2():
            global a
            a = a + b
            return a
        # If return just "foo", it will work because f1() will be considered inner function.
        # Return f1, then nonlocal inside f1 will not be able to find "a" cell.
        return foo(), f2

    def testObj(self, obj):
        f1, f2 = obj
        tc.assertEqual(f1(), 4)
        tc.assertEqual(f1(), 7)
        tc.assertEqual(f2(), 8)
        tc.assertEqual(f2(), 11)
        tc.assertEqual(f1(), 10)
