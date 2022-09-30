import unittest
tc = unittest.TestCase()

# This works because we wrap both text() and decorator() into the sourcecode
# There will be no pickled on runtime text() or UpperDecorator()

class TestClass():
    def getFunction(self):
        def wrap():
            def UpperDecorator(func):
                def inner():
                    # Add "1" to check for double execution
                    return func().upper() + " 1"
                return inner
            @UpperDecorator
            def text():
                return "hello world"
            return text
        return wrap

    def testObj(self, obj):
        func = obj()
        tc.assertEqual(func(), "HELLO WORLD 1")

# This accidentally works because of the runtime scope, though no global_world is pickled.

global_world = "world"
class TestClass2():
    def getFunction(self):
        def wrap():
            def UpperDecorator(func):
                def inner():
                    return func().upper() + " 1"
                return inner
            @UpperDecorator
            def text():
                return "hello " + global_world
            return text
        return wrap

    def testObj(self, obj):
        func = obj()
        tc.assertEqual(func(), "HELLO WORLD 1")