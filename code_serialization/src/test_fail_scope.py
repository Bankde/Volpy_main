import unittest
tc = unittest.TestCase()

'''
Fail of using complex scope. 
For 2 reasons:
1. codepickle sends code to exec. 
    The endpoint won't know if starting function uses LOAD_DEREF or LOAD_GLOBAL.
    As much as the code can provide, it uses LOAD_GLOBAL.
    So it could mess up with the real global var.
2. It's currently NOT possible to manaully edit bytecode between LOAD_DEREF and LOAD_GLOBAL,
    and it's NOT possible to add more cells (freevar) into already created function. 
    Cloudpickle creates empty cell at the same time of creating dynamic function by also providing
    bytecode and globals. This approach is not possible with the exec method.
'''

a = 10
b = 5
class TestClass():
    def getFunction(self):
        def foo():
            a = 8
            def f1():
                return a+b
            return f1
        def f2():
            return a+b
        return foo(), f2

    def testObj(self, obj):
        f1, f2 = obj
        tc.assertEqual(f1(), 13)
        tc.assertEqual(f2(), 15)

# Incorrect closure scope after deserialization (thus no exception after deserialize)
class TestClass2():
    def getFunction(self):
        def f():
            if False:  # pragma: no cover
                cell = None
            def g():
                cell  # NameError, unbound free variable
            return g
        return f()

    def testObj(self, obj):
        g1 = obj
        tc.assertRaises(NameError, g1)
