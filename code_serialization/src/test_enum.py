import unittest
tc = unittest.TestCase()

'''
The serialization result is analogous to the cloudpickle that
    1. The deserialized enum will be merged into the existing enum. (id no changes)
    2. The deserialized function will replaced the enum's function. (id changes)
The error from cloudpickle comes from the test trying to dump the loaded function.
'''

class TestClass():
    def getFunction(self):
        import enum
        class StringEnum(str, enum.Enum):
            """Enum when all members are also (and must be) strings"""

        class Color(StringEnum):
            """3-element color space"""
            RED = "1"
            GREEN = "2"
            BLUE = "3"

            def is_green(self):
                return self is Color.GREEN

        return [Color.GREEN, Color.GREEN, Color]

        # codepickle systematically tracks provenance of class definitions
        # and ensure reconciliation in case of round trips:
        assert green1 is Color.GREEN
        assert ClonedColor is Color

        codepickle.dumps(Color.GREEN)

    def testObj(self, obj):
        green1, green2, ClonedColor = obj
        assert green1 is green2
        assert green1 is ClonedColor.GREEN
        assert green1 is not ClonedColor.BLUE
        assert isinstance(green1, str)
        assert green1.is_green()
