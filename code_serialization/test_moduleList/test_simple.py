import codepickle
import unittest

class SimpleModuleTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        codepickle.set_config_get_import(True)

    def test_simple(self):
        import numpy
        const = 100
        def array_const(size):
            return numpy.zeros(size) + const

        pickled, modules = codepickle.dumps(array_const)
        self.assertEqual(len(modules), 1)
        self.assertIn("numpy", modules)

    def test_alias(self):
        import numpy as np
        const = 100
        def array_const(size):
            return np.zeros(size) + const

        pickled, modules = codepickle.dumps(array_const)
        self.assertEqual(len(modules), 1)
        self.assertIn("numpy", modules)

    def test_unused(self):
        import numpy as np
        import pandas
        const = 100
        def array_const(size):
            return np.zeros(size) + const

        pickled, modules = codepickle.dumps(array_const)
        self.assertEqual(len(modules), 1)
        self.assertIn("numpy", modules)
        self.assertNotIn("pandas", modules)

if __name__ == '__main__':
    unittest.main()