from abc import ABC

import attr


@attr.s
class Skeleton:
    segments = attr.ib()


class Segment(ABC):
    pass


@attr.s
class Blank(Segment):
    solution = attr.ib()


@attr.s
class Given(Segment):
    code = attr.ib()
