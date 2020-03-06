import datetime
from typing import NamedTuple, Optional


class Config(NamedTuple):

    """
    Class with final config parameters such as:
    - report_size: size of report
    - report_dir: directory where report will be constructed
    - log_dir: directory where to take logs from
    """

    report_size: int
    report_dir: str
    log_dir: str
    log_file: str
    failures_percent_threshold: float


class LatestLogFile(NamedTuple):

    """
    Class with latest log file parameters such as:
    - path path to latest log file
    - create_date creation date
    - extension file extension
    """

    path: str
    date_of_creation: datetime.date
    extension: str


class SingleLogParserResult(NamedTuple):

    """
    Class with result data of single line parsing such as:
    - url - visited url
    - time - spent time on certain url
    - error - if there was any error during parsing line
    """

    url: Optional[str]
    time: Optional[float]
    is_failed: bool
