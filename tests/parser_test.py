import random
import unittest

from skeletonize.parser import (
    SkeletonParser,
    TooLongDelimiterException,
    ExtraDelimiterException,
)
from skeletonize.skeleton import Skeleton, Blank, Given


class ParserTest(unittest.TestCase):
    def test_just_skeleton(self):
        self.assertEqual(
            SkeletonParser().parse("{{hi hi hi}}"), Skeleton([Blank("hi hi hi")])
        )
        self.assertEqual(
            SkeletonParser().parse("{{can contain } character}}"),
            Skeleton([Blank("can contain } character")]),
        )
        # can be empty
        self.assertEqual(SkeletonParser().parse("{{}}"), Skeleton([Blank("")]))
        self.assertEqual(
            SkeletonParser().parse("{{multi\nline}}"), Skeleton([Blank("multi\nline")]),
        )
        self.assertEqual(
            SkeletonParser(start_char="*", end_char="}").parse("**customizable}}"),
            Skeleton([Blank("customizable")]),
        )

        self.assertEqual(
            SkeletonParser(number_to_match=3).parse("{{{customizable length}}}"),
            Skeleton([Blank("customizable length")]),
        )

    def test_too_long(self):
        self.assertRaises(
            TooLongDelimiterException, lambda: SkeletonParser().parse("{{{}}}")
        )
        self.assertRaises(
            TooLongDelimiterException,
            lambda: SkeletonParser().parse("{{{{'nested block'}}}}"),
        )
        self.assertRaises(
            TooLongDelimiterException,
            lambda: SkeletonParser().parse("{{{which way is this extra one grouped?}}"),
        )
        self.assertRaises(
            TooLongDelimiterException, lambda: SkeletonParser().parse("unmatched {{{"),
        )

    def test_unmatched(self):
        self.assertRaises(
            ExtraDelimiterException,
            lambda: SkeletonParser().parse("{{hi}} {{unmatched"),
        )
        self.assertRaises(
            ExtraDelimiterException,
            lambda: SkeletonParser().parse("{{hi}} unmatched}}"),
        )
        self.assertRaises(
            ExtraDelimiterException,
            lambda: SkeletonParser().parse("{{hi unmatched {{ inside}}"),
        )

        self.assertRaises(
            ExtraDelimiterException,
            lambda: SkeletonParser().parse("{{nested {{ delimiters }} don't work }}"),
        )

    def test_no_skeleton(self):
        self.assertEqual(
            SkeletonParser().parse("hi hi hi"), Skeleton([Given("hi hi hi")])
        )
        self.assertEqual(
            SkeletonParser().parse("new\nline"), Skeleton([Given("new\nline")])
        )
        self.assertEqual(
            SkeletonParser().parse("can have { these } characters"),
            Skeleton([Given("can have { these } characters")]),
        )

    def test_blank_surrounded_by_given(self):
        self.assertEqual(
            SkeletonParser().parse("hi {{hi}} hi"),
            Skeleton([Given("hi "), Blank("hi"), Given(" hi")]),
        )
        self.assertEqual(
            SkeletonParser().parse("hi {{hi}}"), Skeleton([Given("hi "), Blank("hi")]),
        )
        self.assertEqual(
            SkeletonParser().parse("hi {{hi}}\n"),
            Skeleton([Given("hi "), Blank("hi"), Given("\n")]),
        )
        self.assertEqual(
            SkeletonParser().parse("hi {{hi}} "),
            Skeleton([Given("hi "), Blank("hi"), Given(" ")]),
        )

    def test_multiple_blanks(self):
        self.assertEqual(
            SkeletonParser().parse("{{hi}} * {{bye}}"),
            Skeleton([Blank("hi"), Given(" * "), Blank("bye")]),
        )
        self.assertEqual(
            SkeletonParser().parse("{{adjacent}}{{blanks}}"),
            Skeleton([Blank("adjacent"), Blank("blanks")]),
        )

    def fuzz_test(self):
        items = "x", " ", "{", "{{", "{{{", "}}}", "}}", "}"
        for _ in range(1000):
            length = random.randint(0, 10)
            string = "".join(random.choice(items) for _ in range(length))

            try:
                SkeletonParser().parse(string)
            except TooLongDelimiterException:
                pass
            except ExtraDelimiterException:
                pass
