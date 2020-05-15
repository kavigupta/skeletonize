import re
from functools import cached_property

from skeletonize.skeleton import Given, Skeleton, Blank


class SkeletonParser:
    def __init__(self, start="<<<", end=">>>"):
        self.start = start
        self.end = end

    def parse(self, skeleton_code):
        chunks = []
        index = 0
        for match in self._pattern.finditer(skeleton_code):
            if match.start() != index:
                chunks.append(Given(skeleton_code[index: match.start()]))
            chunks.append(Blank(match.group(1)))
            index = match.end()
        if index != len(skeleton_code):
            chunks.append(Given(skeleton_code[index:]))
        return Skeleton(chunks)

    @cached_property
    def _pattern(self):
        return re.compile(r"{}(.*?){}".format(re.escape(self.start), re.escape(self.end)), flags=re.M | re.S)
