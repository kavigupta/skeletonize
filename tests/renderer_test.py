import unittest

from skeletonize.parser import SkeletonParser
from skeletonize.renderer import UnderscoreBlankRenderer


class UnderscoresRendererTest(unittest.TestCase):
    @staticmethod
    def render_code(code, renderer):
        return SkeletonParser().parse(code).render(renderer)

    def underscores_renderer_test(self):
        self.assertEqual(
            self.render_code("f(<<<x>>>, <<<y>>>)", UnderscoreBlankRenderer()),
            "f(______, ______)",
        )
        self.assertEqual(
            self.render_code(
                "f(<<<x>>>, <<<y>>>)", UnderscoreBlankRenderer(blank_size=8)
            ),
            "f(________, ________)",
        )
        self.assertEqual(
            self.render_code(
                "<<<multi line\n blank>>>", UnderscoreBlankRenderer()
            ),
            "______",
        )
