import re
import string
from abc import abstractmethod, ABC

import attr

from skeletonize.skeleton import Skeleton, Blank, Given


class Reskeletonizer(ABC):
    @abstractmethod
    def reskeletonize(self, skeleton: Skeleton, code: str) -> Skeleton:
        pass


@attr.s
class RegexReskeletonizer(Reskeletonizer):
    ignore_whitespace = attr.ib(default=True)
    """
    Reskeletonizer that uses character-level matching to match given portions the skeleton
        in the provided code, in order to find blanks.

    Arguments
        ignore_whitespace: whether to ignore whitespace when resolving blanks. Default True
        allow_errors: whether to allow deviations from the skeleton (return a ErrorBlank segments). Default True
    """

    def reskeletonize(self, skeleton: Skeleton, code: str) -> Skeleton:
        match = self.create_regex(skeleton).match(code)
        if not match:
            raise CannotReskeletonizeException

        blanks = match.groups()
        assert len(blanks) == len(skeleton.segments)

        new_segments = []
        for segment, content in zip(skeleton.segments, blanks):
            if isinstance(segment, Blank):
                new_segments.append(Blank(content))
            elif isinstance(segment, Given):
                new_segments.append(Given(content))
            else:
                raise AssertionError("Should be unreachable")

        return Skeleton(new_segments)

    def create_regex(self, skeleton):
        regex_chunks = ["^"]
        for segment in skeleton.segments:
            regex_chunks.append(segment.matcher_regex(self._match_given_text))
        regex_chunks.append("$")
        pattern = "".join(regex_chunks)
        return re.compile(pattern, re.DOTALL)

    def _match_given_text(self, code):
        if not self.ignore_whitespace:
            return re.escape(code)
        return r"\s+".join(re.escape(word) for word in re.split(r"\s", code))

    def _is_junk(self, x):
        if self.ignore_whitespace:
            return x in string.whitespace
        return False


class CannotReskeletonizeException(Exception):
    pass
