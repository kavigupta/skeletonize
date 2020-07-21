import unittest
from textwrap import dedent

from skeletonize.reskeletonize import normalize_python

class NormalizerTest(unittest.TestCase):
    def test_module_docstring(self):
        input = dedent(
            """
            '''
            docstring here!
            '''
            x = 2
            module_code_goes_here
            '''
            another docstring


            here


            hi!

            '''
            """
        )
        result = dedent(
            """
            '[ommited docstring]'
            x = 2
            module_code_goes_here
            '[ommited docstring]'
            """
        )
        self.assertEqual(result, normalize_python(input))

    def test_function_docstring(self):
        input = dedent(
            """
            def f(x):
                '''
                hi this is a docstring
                '''
                x = "hi this is not a docstring"
            """
        )
        result = dedent(
            """

            def f(x):
                '[ommited docstring]'
                x = 'hi this is not a docstring'
            """
        )
        self.assertEqual(result, normalize_python(input))
