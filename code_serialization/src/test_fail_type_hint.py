import unittest
import typing
tc = unittest.TestCase()

'''
Similar to decorator. Type hint becomes function properties during the dynamic interpretion.
Thus; there is no information linking from type_ => typing.TypeVar('T') nor typing module.
The information in runtime is `'__annotations__': {'arg': ~T, 'return': ~T}`
This limitation is similar to decorator.
'''

type_ = typing.TypeVar('T')

def check_annotations(obj, expected_type):
    assert obj.__annotations__["attribute"] == expected_type
    assert obj.method.__annotations__["arg"] == expected_type
    assert obj.method.__annotations__["return"] == expected_type
    return "ok"

class TestClass():
    def getFunction(self):
        class MyClass:
            def method(self, arg: typing.Any) -> typing.Any:
                return arg
        MyClass.__annotations__ = {'attribute': typing.Any}
        obj = MyClass()
        return obj

    def testObj(self, obj):
        assert check_annotations(obj, type_) == "ok"