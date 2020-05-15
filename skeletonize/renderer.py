from abc import ABC, abstractmethod

import attr


class SkeletonRenderer(ABC):
    @abstractmethod
    def combine(self, per_segment_outputs):
        pass

    @abstractmethod
    def render_blank(self, blank):
        pass

    @abstractmethod
    def render_given(self, given):
        pass


@attr.s
class UnderscoreBlankRenderer(SkeletonRenderer):
    blank_size = attr.ib(default=6)

    def combine(self, per_segment_outputs):
        return "".join(per_segment_outputs)

    def render_blank(self, blank):
        return "_" * self.blank_size

    def render_given(self, given):
        return given.code
