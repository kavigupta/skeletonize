from functools import lru_cache

from .skeleton import Skeleton, Given, Insertion, Deletion, Blank, Correction


def align_skeleton(skeleton, code, is_whitespace):
    """
    Aligns the given skeleton with the given code. This algorithm minimizes
        the edit distance (just insert/delete) of all the Given portions of
        the skeleton with that of the code.
    """
    segments = [x.code if isinstance(x, Given) else Blank for x in skeleton.segments]

    @lru_cache(None)
    def helper_align(segment_idx, within_segment_idx, code_idx):
        """
        Aligns the given skeletal segments with the code.

        Returns (match, cost)
            match: the sequence of corrections as a linked list of tuples
            cost: the cost of the corrections, in edits
        """
        if segment_idx == len(segments) and code_idx == len(code):
            return (), 0
        if segment_idx > len(segments) or code_idx > len(code):
            return None, float("inf")

        segm = segments[segment_idx] if segment_idx < len(segments) else None
        code_char = code[code_idx] if code_idx < len(code) else None

        if segm is Blank:
            possibilities = []

            # do not use blank
            possibilities.append(helper_align(segment_idx + 1, 0, code_idx))

            # use blank?
            if code_idx < len(code):
                s, c = helper_align(segment_idx, within_segment_idx, code_idx + 1)
                new_s = Blank(code_char), s
                possibilities.append((new_s, c))

            return min(possibilities, key=lambda x: x[1])

        if segm is not None and within_segment_idx == len(segm):
            return helper_align(segment_idx + 1, 0, code_idx)

        segm_char = segm[within_segment_idx] if segm is not None else None

        possibilities = []
        # match?
        if segm_char == code_char:
            s, c = helper_align(segment_idx, within_segment_idx + 1, code_idx + 1)
            new_s = Given(code_char), s
            possibilities.append((new_s, c))

        # insert?
        if code_char is not None:
            s, c = helper_align(segment_idx, within_segment_idx, code_idx + 1)
            if is_whitespace and code_char.isspace():
                res = (Given(code_char), s), c
            else:
                res = (Insertion(code_char), s), c + 1
            possibilities.append(res)

        # delete
        if segm_char is not None:
            s, c = helper_align(segment_idx, within_segment_idx + 1, code_idx)
            if is_whitespace and segm_char.isspace():
                res = (Given(segm_char), s), c
            else:
                res = (Deletion(segm_char), s), c + 1
            possibilities.append(res)

        return min(possibilities, key=lambda x: x[1])

    s, _ = helper_align(0, 0, 0)
    return Skeleton(consolidate(to_list(s)))


def to_list(ll):
    result = []
    while ll:
        result.append(ll[0])
        ll = ll[1]
    return result


def consolidate(segments):
    result = []
    for x in segments:
        if not result or type(result[-1]) != type(x):
            result.append(x)
            continue
        if isinstance(x, (Given, Correction)):
            result[-1] = type(x)(result[-1].code + x.code)
        elif isinstance(x, Blank):
            result[-1] = type(x)(result[-1].solution + x.solution)
        else:
            raise AssertionError("unreachable")
    return result
