import unittest
tc = unittest.TestCase()

# Bundle both into same dict to utilize memo will NOT work because
# 1. This is not about memo (sharing var), this is about execution scope
# 2. `text` and `UpperDecorator` has no properties reference to each other, thus no memo anyway.
# 3. While it is possible to manaully add UpperDecorator to text()'s globals, 
#        this is not the main of our project so we decide to leave that to the future research.
#        This approach is incorrect anyway because the decorator would be applied twice.
# 4. Actual correct solution is to remove the decorator line in the src because the decorator
#        effect has already been applied into the function properties.

class TestClass():
    def getFunction(self):
        def UpperDecorator(func):
            def inner():
                return func().upper()
            return inner
        @UpperDecorator
        def text():
            return "hello world"
        return text

    def testObj(self, obj):
        tc.assertEqual(obj(), "HELLO WORLD")

class TestClass2():
    # test_final_or_classvar_misdetection
    def getFunction(self):
        class MyClass:
            @property
            def __type__(self):
                return int
        return MyClass()

    def testObj(self, obj):
        # Only test for picklable
        pass