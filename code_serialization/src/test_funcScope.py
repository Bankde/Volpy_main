import unittest
tc = unittest.TestCase()

g = 300
class TestClass():
    def getFunction(self):
        def funcA():
            global g
            g = g+1
            return g
        def funcB():
            global g
            g = g*2
            return g
        return [funcA, funcB]

    def testObj(self, obj):
        f1, f2 = obj
        tc.assertEqual(f1(), 301)
        tc.assertEqual(f2(), 602)
        tc.assertEqual(f1(), 603)
        tc.assertEqual(f1(), 604)
        tc.assertEqual(f2(), 1208)

# Check that it doesn't use globals
h = 400
class TestClass2():
    def getFunction(self):
        def foo(h):
            def funcA():
                nonlocal h
                h = h+1
                return h
            def funcB():
                nonlocal h
                h = h*2
                return h
            return [funcA, funcB]
        return foo

    def testObj(self, obj):
        f1, f2 = obj(300)
        tc.assertEqual(f1(), 301)
        tc.assertEqual(f2(), 602)
        tc.assertEqual(f1(), 603)
        tc.assertEqual(f2(), 1206)