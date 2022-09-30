import unittest
tc = unittest.TestCase()

class TestClass():
    def getFunction(self):
        class Base:
            def method(self):
                return 1

        class Derived(Base):
            "Derived Docstring"
            def method(self):
                return super().method() + 1
        return Derived

    def testObj(self, obj):
        tc.assertEqual(obj().method(), 2)