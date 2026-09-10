from sources.base import JobSource, RawJob
from sources.source1 import RemotiveSource
from sources.source2 import ArbeitnowSource
from sources.source3 import RssSource

ALL_SOURCES: list[JobSource] = [RemotiveSource(), ArbeitnowSource(), RssSource()]

__all__ = ["ALL_SOURCES", "JobSource", "RawJob"]
