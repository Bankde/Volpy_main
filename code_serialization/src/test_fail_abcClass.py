import unittest
tc = unittest.TestCase()

import abc
class TestClass():
    def getFunction(self):
        class AbstractClass(abc.ABC):
            @abc.abstractmethod
            def some_method(self):
                """A method"""

            @abc.abstractclassmethod
            def some_classmethod(cls):
                """A classmethod"""

            @abc.abstractstaticmethod
            def some_staticmethod():
                """A staticmethod"""

            @abc.abstractproperty
            def some_property(self):
                """A property"""
                
        class ConcreteClass(AbstractClass):
            def some_method(self):
                return 'it works!'

            @classmethod
            def some_classmethod(cls):
                assert cls == ConcreteClass
                return 'it works!'

            @staticmethod
            def some_staticmethod():
                return 'it works!'

            @property
            def some_property(self):
                return 'it works!'
        return ConcreteClass

    def testObj(self, obj):
        Cls = obj
        inst = Cls()
        tc.assertEqual(inst.some_method(), 'it works!')
        tc.assertEqual(Cls.some_classmethod(), 'it works!')
        tc.assertEqual(Cls.some_staticmethod(), 'it works!')
        tc.assertEqual(inst.some_property, 'it works!')