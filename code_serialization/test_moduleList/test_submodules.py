import codepickle
import unittest

class SubmoduleTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        codepickle.set_config_get_import(True)

    def test_simple(self):
        import numpy.random
        const = 1
        def randomIntPlusOne(maxInt):
            numpy.random.seed(0)
            return numpy.random.randint(maxInt) + const

        pickled, modules = codepickle.dumps(randomIntPlusOne)
        self.assertEqual(len(modules), 1)
        self.assertIn("numpy", modules)

    def test_alias(self):
        import numpy.random as random
        const = 1
        def randomIntPlusOne(maxInt):
            random.seed(0)
            return random.randint(maxInt) + const

        pickled, modules = codepickle.dumps(randomIntPlusOne)
        self.assertEqual(len(modules), 1)
        self.assertIn("numpy", modules)

    def test_duplicate(self):
        import numpy.random as random
        import numpy.fft as fft
        const = 1
        def testRandom(size):
            random.seed(0)
            return fft.fft(random.randint(0,2, size=4)) + const

        pickled, modules = codepickle.dumps(testRandom)
        self.assertEqual(len(modules), 1)
        self.assertIn("numpy", modules)

if __name__ == '__main__':
    unittest.main()