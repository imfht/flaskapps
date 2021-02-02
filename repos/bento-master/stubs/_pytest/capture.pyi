import collections


CaptureResult = collections.namedtuple("CaptureResult", ["out", "err"])


class CaptureFixture:
    def readouterr(self) -> CaptureResult:
        ...