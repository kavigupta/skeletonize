import random
import string
import unittest

from skeletonize.parser import SkeletonParser
from skeletonize.renderer import (
    UnderscoreBlankRenderer,
    DisplaySolutionsRenderer,
    render_with_identifiers,
    parse_identifiers,
    DuplicateIdentifierException,
)
from skeletonize.skeleton import Blank


class UnderscoresRendererTest(unittest.TestCase):
    @staticmethod
    def render_code(code, renderer):
        return SkeletonParser().parse(code).render(renderer)

    def underscores_renderer_test(self):
        self.assertEqual(
            self.render_code("f({{x}}, {{y}})", UnderscoreBlankRenderer()),
            "f(______, ______)",
        )
        self.assertEqual(
            self.render_code("f({{x}}, {{y}})", UnderscoreBlankRenderer(blank_size=8)),
            "f(________, ________)",
        )
        self.assertEqual(
            self.render_code("{{multi line\n blank}}", UnderscoreBlankRenderer()),
            "______",
        )


class DisplaySolutionsRendererTest(unittest.TestCase):
    @staticmethod
    def render_code(code, renderer):
        return SkeletonParser().parse(code).render(renderer)

    def underscores_renderer_test(self):
        self.assertEqual(
            self.render_code("a {{b}} c", DisplaySolutionsRenderer()), "a {{b}} c"
        )
        self.assertEqual(
            self.render_code(
                "a {{b}} c", DisplaySolutionsRenderer(start="!!!", end="***")
            ),
            "a !!!b*** c",
        )


class TestIdentiferRenderer(unittest.TestCase):
    def single_variable_renderer_test(self):
        code, ids = render_with_identifiers(SkeletonParser().parse("{{x}}"))
        [x] = ids
        self.assertEqual(x, code)
        self.assertEqual(ids[x], Blank("x"))

    def multiple_variable_renderer_test(self):
        code, ids = render_with_identifiers(SkeletonParser().parse("{{x}} + {{y}}"))
        inverse_ids = {blank.solution: ident for ident, blank in ids.items()}
        self.assertCountEqual(inverse_ids, "xy")
        self.assertEqual(code, inverse_ids["x"] + " + " + inverse_ids["y"])

    def test_format(self):
        for _ in range(100):
            length = random.randint(1, 100)
            _, [ident] = render_with_identifiers(
                SkeletonParser().parse("{{x}}"), identifier_length=length
            )
            self.assertRegex(ident, "^[a-z]{%s}$" % length)

    def parse_ident_skeleton_test(self):
        self.assertEqual(
            parse_identifiers("x + y", {"x": Blank("2 + 3"), "y": Blank("-23")}).render(
                DisplaySolutionsRenderer()
            ),
            "{{2 + 3}} + {{-23}}",
        )

        self.assertRaises(
            DuplicateIdentifierException,
            lambda: parse_identifiers(
                "x + x", {"x": Blank("2 + 3"), "y": Blank("-23")}
            ).render(DisplaySolutionsRenderer()),
        )

    def fuzz_test(self):
        for _ in range(1000):
            components = []
            for _ in range(10):
                items = "".join(
                    random.choice(string.printable)
                    for _ in range(random.randint(0, 20))
                )
                items = items.replace("{", "").replace("}", "")
                if random.randint(0, 1):
                    items = "{{" + items + "}}"
                components.append(items)
            result = "".join(components)
            code, ids = render_with_identifiers(SkeletonParser().parse(result))
            self.assertNotIn("{{", code)
            self.assertNotIn("}}", code)
            code = parse_identifiers(code, ids).render(DisplaySolutionsRenderer())
            self.assertEqual(result, code)
