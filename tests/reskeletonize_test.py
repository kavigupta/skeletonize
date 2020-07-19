import unittest

from skeletonize.parser import SkeletonParser
from skeletonize.renderer import DisplaySolutionsRenderer
from skeletonize.reskeletonize import (
    Reskeletonizer,
    normalize_python,
)


class ReskeletonizerTest(unittest.TestCase):
    @staticmethod
    def parse_skeleton(code, skeleton_code, **kwargs):
        return (
            Reskeletonizer(**kwargs)
            .reskeletonize(SkeletonParser().parse(skeleton_code), code)
            .render(DisplaySolutionsRenderer())
        )

    def basic_reskeleton_test(self):
        skeleton_code = "x = lambda {{x}}: {{x * 2}}"
        self.assertEqual(
            self.parse_skeleton("x = lambda y: y * 2", skeleton_code),
            "x = lambda {{y}}: {{y * 2}}",
        )
        self.assertEqual(
            self.parse_skeleton("x = lambda y:    y * 2", skeleton_code),
            "x = lambda {{y}}: {{   y * 2}}",
        )
        self.assertEqual(
            self.parse_skeleton("x = lambda y, z: y * z", skeleton_code),
            "x = lambda {{y, z}}: {{y * z}}",
        )
        self.assertEqual(
            self.parse_skeleton("x = lambda y, z: y \n* z", skeleton_code),
            "x = lambda {{y, z}}: {{y \n* z}}",
        )
        self.assertEqual(
            self.parse_skeleton("something utterly unrelated", skeleton_code),
            "<<-x = lambda >>{{something}}<<-:>> {{utterly unrelated}}",
        )
        # extra whitespace
        self.assertEqual(
            self.parse_skeleton("x     =    lambda y, z: y * z", skeleton_code),
            "x <<+    >>= <<+   >>lambda {{y, z}}: {{y * z}}",
        )

        # quotation
        self.assertEqual(self.parse_skeleton(".x.", ".{{between dots}}."), ".{{x}}.")

        self.assertEqual(
            self.parse_skeleton(".{{between dots}}.", "axa"),
            "<<+.{{between dots}}.>><<-axa>>",
        )

    def parenthesized_reskeleton_test(self):
        skeleton_code = "{{x}} * {{y}} * {{z}}"
        self.assertEqual(
            self.parse_skeleton("a * b * c", skeleton_code), "{{a}} * {{b}} * {{c}}",
        )
        self.assertEqual(
            self.parse_skeleton("a * (b * c)", skeleton_code),
            "{{a}} * {{(b}} * {{c)}}",
        )
        self.assertEqual(
            self.parse_skeleton("a * b * c * d", skeleton_code),
            "{{a}} * {{b}} * {{c * d}}",
        )
        self.assertEqual(
            self.parse_skeleton("a + b * c * d", skeleton_code),
            "{{a + b}} * {{c}} * {{d}}",
        )

    def reskeleton_with_more_whitespace_test(self):
        skeleton_code = "x = lambda {{x}}: {{x * 2}}"
        self.assertEqual(
            self.parse_skeleton(
                "x     =    lambda y, z: y * z", skeleton_code, ignore_whitespace=True
            ),
            "x     =    lambda {{y, z}}: {{y * z}}",
        )
        self.assertEqual(
            self.parse_skeleton(
                "x     =    lambda y, z: y \n* z", skeleton_code, ignore_whitespace=True
            ),
            "x     =    lambda {{y, z}}: {{y \n* z}}",
        )
        self.assertEqual(
            self.parse_skeleton(
                "x     =    \nlambda y, z: y * z", skeleton_code, ignore_whitespace=True
            ),
            "x     =    \nlambda {{y, z}}: {{y * z}}",
        )

    def normalize_python_test(self):
        self.assertEqual(normalize_python("x = 2 + (3)"), "\nx = (2 + 3)\n")
        self.assertEqual(normalize_python("x = 2 * 3 + 4"), "\nx = ((2 * 3) + 4)\n")

    def reskeleton_python_ast_test(self):
        skeleton_code = "x = 2 + {{three}}"
        self.assertEqual(
            self.parse_skeleton(
                "x = (2) + 3",
                skeleton_code,
                ignore_whitespace=True,
                normalizer=normalize_python,
            ),
            "\nx = (2 + {{3}})\n",
        )
        self.assertEqual(
            self.parse_skeleton(
                "x \\\n    = (2) + 3",
                skeleton_code,
                ignore_whitespace=True,
                normalizer=normalize_python,
            ),
            "\nx = (2 + {{3}})\n",
        )
        self.assertEqual(
            self.parse_skeleton(
                "# a comment\nx = (2) + 3",
                skeleton_code,
                ignore_whitespace=True,
                normalizer=normalize_python,
            ),
            "\nx = (2 + {{3}})\n",
        )

    def deformat_skeleton_and_code_test(self):
        skeleton_code = "def f(x): # function that does some stuff\n return f ({{x}})"
        self.assertEqual(
            self.parse_skeleton(
                "def f          (x): return f(6)",
                skeleton_code,
                ignore_whitespace=True,
                normalizer=normalize_python,
            ),
            "\n\ndef f(x):\n    return f({{6}})\n",
        )
