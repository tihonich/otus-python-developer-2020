import datetime
import os
import unittest
from typing import NoReturn, Tuple

from log_analyzer import LOG_FILE_PATTERN
from log_analyzer import find_latest_log, parse_log_file, calculate_url_stats
from models import Config, LatestLogFile


class TestLatestLogFileFinder(unittest.TestCase):

    """
    Class for testing finder of latest log files
    """

    TEST_FOLDER_NAME = "./test_folder"

    def setUp(self) -> NoReturn:

        """
        Creates test folder
        :return:
        """

        os.mkdir(TestLatestLogFileFinder.TEST_FOLDER_NAME)
        self.test_folder = TestLatestLogFileFinder.TEST_FOLDER_NAME

    def tearDown(self) -> NoReturn:

        """
        Deletes all files from test folder and folder itself
        """

        for file in os.scandir(TestLatestLogFileFinder.TEST_FOLDER_NAME):
            os.remove(os.path.join(TestLatestLogFileFinder.TEST_FOLDER_NAME, file.name))
        os.rmdir(TestLatestLogFileFinder.TEST_FOLDER_NAME)

    def _prepare_test_log_files(self, test_files_names: Tuple[str]) -> NoReturn:

        """
        Creates files for testing finding latest log function
        :param test_files_names: tuple of files to prepare
        """

        test_log_files_path_names = tuple(map(
            lambda file_name: os.path.join(self.test_folder, file_name),
            test_files_names
        ))

        for test_log_file_name in test_log_files_path_names:
            with open(test_log_file_name, "w", encoding="utf-8"):
                pass

    def test_finding_latest_log_file(self):

        """
        Tests finding latest log file (file with latest date in file name
        """

        self._prepare_test_log_files(
            ("nginx-access-ui.log-20170830.gz",
             "nginx-access-ui.log-20170701.gz",
             "nginx-access-ui.log-19851117.gz",
             "nginx-access-ui.log-20180630.gz",
             "nginx-access-ui.log-20191104.gz")
        )

        latest_log_file = find_latest_log(
            log_dir=self.test_folder,
            log_file_pattern=LOG_FILE_PATTERN
        )

        right_file_name = os.path.join(self.test_folder, "nginx-access-ui.log-20191104.gz")
        right_date = datetime.datetime(year=2019, month=11, day=4)

        with self.subTest():
            self.assertEqual(right_file_name, latest_log_file.path)
        with self.subTest():
            self.assertEqual(".gz", latest_log_file.extension)
        with self.subTest():
            self.assertEqual(right_date, latest_log_file.date_of_creation)

    def test_ignoring_wrong_formats(self):

        """
        Tests that all file formats except .gz, .txt, .log are ignored
        while searching latest log file
        """

        # File with right format has earliest date
        self._prepare_test_log_files(
            ("nginx-access-ui.log-20160101.txt",
             "nginx-access-ui.log-20190804.zip",
             "nginx-access-ui.log-20190904.rtf",
             "nginx-access-ui.log-20191004.csv",
             "nginx-access-ui.log-20191104.bz2")
        )

        latest_log_file = find_latest_log(
            log_dir=self.test_folder,
            log_file_pattern=LOG_FILE_PATTERN
        )

        right_file_name = os.path.join(self.test_folder, "nginx-access-ui.log-20160101.txt")
        right_date = datetime.datetime(year=2016, month=1, day=1)

        with self.subTest():
            self.assertEqual(right_file_name, latest_log_file.path)
        with self.subTest():
            self.assertEqual(".txt", latest_log_file.extension)
        with self.subTest():
            self.assertEqual(right_date, latest_log_file.date_of_creation)

    def test_suitable_log_file_not_found(self):

        """
        Tests if function returns nothing if suitable log file not found
        """

        # No suitable log file
        self._prepare_test_log_files(
            ("nginx-access-ui.log-20190804.zip",
             "nginx-access-ui.log-20190904.rtf",
             "nginx-access-ui.log-20191004.csv",
             "nginx-access-ui.log-20191104.bz2")
        )

        latest_log_file = find_latest_log(
            log_dir=self.test_folder,
            log_file_pattern=LOG_FILE_PATTERN
        )

        self.assertIsNone(latest_log_file)


class TestUrlStatsCalculator(unittest.TestCase):

    """
    Class for testing calculator of url stats
    """

    TEST_CONFIG = Config(
        report_size=50,
        report_dir="./reports",
        log_dir="./nginx_logs",
        log_file="./script_logs/test.log",
        failures_percent_threshold=50.0
    )

    LOG_FILE = LatestLogFile(
        path="./nginx_logs/test_sample.txt",
        date_of_creation=datetime.date(year=2019, month=11, day=5),
        extension=".txt"
    )

    def test_url_stats_size(self):

        """
        Tests if url stats size coincides with report size from config
        :return:
        """
        parsed_line_gen = parse_log_file(
            log_file=TestUrlStatsCalculator.LOG_FILE,
            log_file_opener=open
        )
        url_stats = calculate_url_stats(
            parsed_line_gen=parsed_line_gen,
            cfg=TestUrlStatsCalculator.TEST_CONFIG
        )

        with self.subTest():
            self.assertEqual(TestUrlStatsCalculator.TEST_CONFIG.report_size, len(url_stats))

        urls = set()
        for single_url_stat in url_stats:
            urls.add(single_url_stat["url"])

        with self.subTest():
            self.assertEqual(TestUrlStatsCalculator.TEST_CONFIG.report_size, len(urls))

        with self.subTest():
            for single_url_stat in url_stats:
                self.assertIn("url", single_url_stat)
                self.assertIn("count", single_url_stat)
                self.assertIn("count_perc", single_url_stat)
                self.assertIn("time_sum", single_url_stat)
                self.assertIn("time_perc", single_url_stat)
                self.assertIn("time_avg", single_url_stat)
                self.assertIn("time_max", single_url_stat)
                self.assertIn("time_med", single_url_stat)

