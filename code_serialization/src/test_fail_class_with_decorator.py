import unittest
tc = unittest.TestCase()

class TestClass():
    def getFunction(self):
        class MyClass():
            @staticmethod
            def test_sm():
                return "sm works"

            @classmethod
            def test_cm(cls):
                return "cm works"
        return MyClass

    def testObj(self, obj):
        tc.assertEqual(obj.test_sm(), "sm works")
        tc.assertEqual(obj.test_cm(), "cm works")