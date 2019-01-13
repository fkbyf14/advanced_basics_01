import unittest
import log_analyzer
import warnings


class LogAnalyzerTest(unittest.TestCase):
    def test_create_parser(self):
        default_config_path = r'C:\Users\user\PycharmProjects\advanced_basics_01\config_root.txt'
        parser = log_analyzer.create_parser(default_config_path)
        self.assertEqual(True, isinstance(parser, log_analyzer.argparse.ArgumentParser))

    def test_get_result_config(self):
        with warnings.catch_warnings():
            warnings.filterwarnings('ignore', category=ResourceWarning)
            config_report_size = r'C:\Users\user\config\test_config_only_reportsize.txt'
            parser = log_analyzer.create_parser(config_report_size)
            expect_config = {"REPORT_SIZE": 300, "REPORT_DIR": r"C:\Users\user\reports",
                             "LOG_DIR": r"C:\Users\user\log\ansi_broken"}
            self.assertEqual(expect_config, log_analyzer.get_result_config(parser, config_report_size))
            config_report_dir = r'C:\Users\user\config\test_config_only_reportdir.txt'
            parser = log_analyzer.create_parser(config_report_dir)
            expect_config = {"REPORT_SIZE": 20, "REPORT_DIR": r"C:\Users\user",
                             "LOG_DIR": r"C:\Users\user\log\ansi_broken"}
            self.assertEqual(expect_config, log_analyzer.get_result_config(parser, config_report_dir))

    def test_search_last_log(self):
        search_tuple = log_analyzer.search_last_log(log_analyzer.config["LOG_DIR"])
        expect_tuple = r'C:\Users\user\log\nginx-access-ui.log-20170308', '2017.03.08'
        self.assertEqual(expect_tuple, search_tuple)

    def test_count_data(self):
        expect_res_table = [{'count': 1, 'time_avg': 0.389, 'time_max': 0.389, 'time_sum': 0.389,
                             'url': '/api/v2/group/1203654/banners', 'time_med': 0.389, 'time_perc': 46.981,
                             'count_perc': 25.0},
                            {'count': 1, 'time_avg': 0.214, 'time_max': 0.214, 'time_sum': 0.214,
                             'url': '/accounts/login/', 'time_med': 0.214, 'time_perc': 25.845, 'count_perc': 25.0},
                            {'count': 1, 'time_avg': 0.134, 'time_max': 0.134, 'time_sum': 0.134,
                             'url': '/api/v2/internal/revenue_share/service/276/partner/75749451/statistic/v2'
                                    '?date_from=2017-06-24&date_to=2017-06 '
                                    '-30&date_type=day',
                             'time_med': 0.134, 'time_perc': 16.184, 'count_perc': 25.0},
                            {'count': 1, 'time_avg': 0.091, 'time_max': 0.091,
                             'time_sum': 0.091,
                             'url': '/api/v2/banner/22217377/statistic/?date_from=2017-06-30&date_to=2017-06-30',
                             'time_med': 0.091, 'time_perc': 10.99, 'count_perc': 25.0}]
        res_table = log_analyzer.count_data(r'C:\Users\user\log\small\nginx-access-ui.log-20170701')
        self.assertEqual(expect_res_table, res_table)


if __name__ == "__main__":
    unittest.main()
