import unittest

from skeletonize.parser import SkeletonParser
from skeletonize.renderer import DisplaySolutionsRenderer
from skeletonize.reskeletonize import (
    RegexReskeletonizer,
    CannotReskeletonizeException,
)


class RegexReskeletonizerTest(unittest.TestCase):
    @staticmethod
    def parse_skeleton(code, skeleton_code, ignore_whitespace=False):
        return (
            RegexReskeletonizer(ignore_whitespace=ignore_whitespace)
            .reskeletonize(SkeletonParser().parse(skeleton_code), code)
            .render(DisplaySolutionsRenderer())
        )

    def basic_reskeleton_test(self):
        skeleton_code = "x = lambda <<<x>>>: <<<x * 2>>>"
        self.assertEqual(
            self.parse_skeleton("x = lambda y: y * 2", skeleton_code),
            "x = lambda <<<y>>>: <<<y * 2>>>",
        )
        self.assertEqual(
            self.parse_skeleton("x = lambda y:    y * 2", skeleton_code),
            "x = lambda <<<y>>>: <<<   y * 2>>>",
        )
        self.assertEqual(
            self.parse_skeleton("x = lambda y, z: y * z", skeleton_code),
            "x = lambda <<<y, z>>>: <<<y * z>>>",
        )
        self.assertEqual(
            self.parse_skeleton("x = lambda y, z: y \n* z", skeleton_code),
            "x = lambda <<<y, z>>>: <<<y \n* z>>>",
        )
        self.assertRaises(
            CannotReskeletonizeException,
            lambda: self.parse_skeleton("something utterly unrelated", skeleton_code),
        )
        # extra whitespace
        self.assertRaises(
            CannotReskeletonizeException,
            lambda: self.parse_skeleton("x     =    lambda y, z: y * z", skeleton_code),
        )

        # quotation
        self.assertEqual(
            self.parse_skeleton(".x.", ".<<<between dots>>>."   ),
            ".<<<x>>>."
        )

        self.assertRaises(
            CannotReskeletonizeException,
            lambda: self.parse_skeleton(".<<<between dots>>>.", "axa")
        )

    def parenthesized_reskeleton_test(self):
        skeleton_code = "<<<x>>> * <<<y>>> * <<<z>>>"
        self.assertEqual(
            self.parse_skeleton("a * b * c", skeleton_code),
            "<<<a>>> * <<<b>>> * <<<c>>>",
        )
        self.assertEqual(
            self.parse_skeleton("a * (b * c)", skeleton_code),
            "<<<a>>> * <<<(b>>> * <<<c)>>>",
        )
        self.assertEqual(
            self.parse_skeleton("a * b * c * d", skeleton_code),
            "<<<a>>> * <<<b>>> * <<<c * d>>>",
        )
        self.assertEqual(
            self.parse_skeleton("a + b * c * d", skeleton_code),
            "<<<a + b>>> * <<<c>>> * <<<d>>>",
        )

    def reskeleton_with_more_whitespace_test(self):
        skeleton_code = "x = lambda <<<x>>>: <<<x * 2>>>"
        self.assertEqual(
            self.parse_skeleton(
                "x     =    lambda y, z: y * z", skeleton_code, ignore_whitespace=True
            ),
            "x     =    lambda <<<y, z>>>: <<<y * z>>>",
        )
        self.assertEqual(
            self.parse_skeleton(
                "x     =    lambda y, z: y \n* z", skeleton_code, ignore_whitespace=True
            ),
            "x     =    lambda <<<y, z>>>: <<<y \n* z>>>",
        )
        self.assertEqual(
            self.parse_skeleton(
                "x     =    \nlambda y, z: y * z", skeleton_code, ignore_whitespace=True
            ),
            "x     =    \nlambda <<<y, z>>>: <<<y * z>>>",
        )
