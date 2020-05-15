from abc import ABC, abstractmethod

import attr

from .renderer import SkeletonRenderer


@attr.s
class Skeleton:
    segments = attr.ib()

    def render(self, renderer: SkeletonRenderer):
        return renderer.combine([segment.render(renderer) for segment in self.segments])


class Segment(ABC):
    @abstractmethod
    def render(self, renderer: SkeletonRenderer):
        pass


@attr.s
class Blank(Segment):
    solution = attr.ib()

    def render(self, renderer: SkeletonRenderer):
        return renderer.render_blank(self)


@attr.s
class Given(Segment):
    code = attr.ib()

    def render(self, renderer: SkeletonRenderer):
        return renderer.render_given(self)
