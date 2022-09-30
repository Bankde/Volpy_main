import unittest
tc = unittest.TestCase()

class TestClass():
    def getFunction(self):
        class Person:
            def __init__(self, fname, lname):
                self.firstname = fname
                self.lastname = lname
            def getHeight(self):
                return 180
            def getName(self):
                return "%s %s" % (self.firstname, self.lastname)
        class Student(Person):
            def getHeight(self):
                return 160
        return Student

    def testObj(self, obj):
        o = obj("First", "Last")
        tc.assertEqual(o.getName(), "First Last")
        tc.assertEqual(o.getHeight(), 160)

class TestClass2():
    def getFunction(self):
        class Person:
            def __init__(self, fname, lname):
                self.firstname = fname
                self.lastname = lname
            def getHeight(self):
                return 180
            def getName(self):
                return "%s %s" % (self.firstname, self.lastname)
        class Student(Person):
            def getHeight(self):
                return 160
        return Student("First", "Last")

    def testObj(self, obj):
        o = obj
        tc.assertEqual(o.getName(), "First Last")
        tc.assertEqual(o.getHeight(), 160)