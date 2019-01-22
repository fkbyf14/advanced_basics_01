#!/usr/bin/env python
# -*- coding: utf-8 -*-


# log_format ui_short '$remote_addr  $remote_user $http_x_real_ip [$time_local] "$request" '
#                     '$status $body_bytes_sent "$http_referer" '
#                     '"$http_user_agent" "$http_x_forwarded_for" "$http_X_REQUEST_ID" "$http_X_RB_USER" '
#                     '$request_time';
import ast
import re
import os
import gzip
import sys
from datetime import datetime
from string import Template
from functools import reduce
import argparse
from collections import Counter, namedtuple
import logging

config = {
    "REPORT_SIZE": 20,
    "REPORT_DIR": "./reports",
    "LOG_DIR": "./log",
    "LOGGING": "./logging/logging",
    "ERRORS LIMIT": 0.5
}

DEFAULT_CONFIG_PATH = "./config_root.txt"
LastLogInfo = namedtuple('Log', ['path', 'date'])


def search_last_log(log_dir):
    """ Ищет свежий лог сервиса nginx-access-ui в формате plain или gzip"""
    if not os.path.isdir(log_dir):
        return None

    the_latest_log_info = None
    for filename in os.listdir(log_dir):
        match = re.match(r'^nginx-access-ui\.log-(?P<date>\d{8})(\.gz)?$', filename)
        if not match:
            continue

        date_string = match.groupdict()['date']
        try:
            log_date = datetime.strptime(date_string, "%Y%m%d")
        except ValueError as e:
            logging.error("ValueError: {0}".format(e))

        if not the_latest_log_info or log_date > the_latest_log_info.log_date:
            the_latest_log_info = LastLogInfo(path=os.path.join(log_dir, filename), date=log_date)
    return the_latest_log_info


def parse_log(path_last_log):
    """функция-генератор, открывает файл лога и считывает построчно"""
    path, extension = os.path.splitext(path_last_log)
    opener = gzip.open if extension == '.gz' else open
    with opener(path_last_log, 'rt', encoding='UTF-8') as log_file:
            for line in log_file:
                yield line


def count_data(path_last_log, errors_limit=None):
    """считает необходимые данные:
    count ‑ сколько раз встречается URL, абсолютное значение
    count_perc ‑ сколько раз встречается URL, в процентнах относительно общего числа запросов
    time_sum ‑ суммарный $request_time для данного URL'а, абсолютное значение
    time_perc ‑ суммарный $request_time для данного URL'а, в процентах относительно общего $request_time всех
    запросов
    time_avg ‑ средний $request_time для данного URL'а
    time_max ‑ максимальный $request_time для данного URL'а
    time_med ‑ медиана $request_time для данного URL'а"""
    pattern_url = re.compile(r'[/\w.*&=\-%?&/]+(?=\sHTTP)')
    pattern_time = re.compile(r'\d+\.\d+$')
    count_of_fail = 0
    list_of_urls = []
    data_of_urls = {}
    request_time_all = 0
    number_of_request = 0
    res_table = []
    try:
        for line in parse_log(path_last_log):
            number_of_request += 1
            time_str = pattern_time.search(line).group()
            url = pattern_url.search(line).group()
            time = float(time_str)
            if url not in list_of_urls:
                data_of_urls[url] = list()
            data_of_urls[url].append(time)
            request_time_all += time
            list_of_urls.append(url)
            index_of_url = list_of_urls.index(url)
            counter = Counter(list_of_urls)
            count = counter[url]
            time_sum = sum(data_of_urls[url])
            time_avg = time_sum / count
            time_max = max(data_of_urls[url])
            sort_time = sorted(data_of_urls[url])
            time_med = sort_time[round(len(data_of_urls[url]) / 2)]
            row_for_table = {"count": count, "time_avg": round(time_avg, 3), "time_max": round(time_max, 3),
                             "time_sum": round(time_sum, 3), "url": url, "time_med": round(time_med, 3)}
            if any(row['url'] for row in res_table) != url:
                res_table.append(row_for_table)
            res_table[index_of_url] = row_for_table
        request_time_all = reduce(lambda x, y: x + y, [row['time_sum'] for row in res_table])
    except AttributeError:
        logging.error("Can't parse, - broken line")
        count_of_fail += 1
    except TypeError as e:
        logging.error("TypeError: {0}".format(e))
    if number_of_request != 0 and count_of_fail / number_of_request > errors_limit:
        logging.info('Level has overrun part_of_fail')
        return
    for row in res_table:
        row['time_perc'] = round(row['time_sum'] * 100 / request_time_all, 3)
        row['count_perc'] = round(row['count'] * 100 / number_of_request, 3)
    sorted_res_table = sorted(res_table, key=lambda row: row['time_sum'], reverse=True)
    return sorted_res_table


def render_template(res_table, report_path):
    with open('report.html', 'rt') as report:
        text = report.read()
    t = Template(text)
    with open(report_path, 'wt', encoding='UTF-8') as report:
        report.write(t.safe_substitute(table_json=res_table))


def create_parser(default_config_path):
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', nargs='?', type=argparse.FileType('r'),
                        default=default_config_path)
    return parser


def get_result_config(parser, default_config):
    args = parser.parse_args()
    with args.config as path_config:
        text_config = path_config.read()
        if not text_config:
            result_config = default_config.copy()
            logging.info("Config from file is empty, I've taken default")
            logging.debug("result config is: {}".format(result_config))
            return result_config

        config_param = re.split('= ', text_config)
        config_from_file = dict(ast.literal_eval(config_param[1]))
        result_config = default_config.copy()
        result_config.update(config_from_file)
        logging.info("Result config = merge of config from file and default")

        return result_config


def main(config):
    the_latest_log_info = search_last_log(result_config["LOG_DIR"])
    if not the_latest_log_info:
        logging.info('No log files yet')
        return

    report_date = the_latest_log_info.date.strftime("%Y.%m.%d")
    report_filename = 'report-{}.html'.format(report_date)
    report_file_path = os.path.join(result_config["REPORT_DIR"], report_filename)

    if os.path.isfile(report_file_path):
        logging.info('Work has already been done')
        return

    result_data_table = count_data(the_latest_log_info.path, config["ERRORS LIMIT"])
    if not result_data_table:
        logging.error('Data not counted')
        return

    render_template(result_data_table[:result_config["REPORT_SIZE"]], report_file_path)


if __name__ == "__main__":
    logging.basicConfig(format='[%(asctime)s] %(levelname).1s %(message)s', level=logging.DEBUG,
                        filename=config["LOGGING"])

    if not os.path.isfile(DEFAULT_CONFIG_PATH):
        logging.info('default_config_path is not available')
    try:
        parser = create_parser(DEFAULT_CONFIG_PATH)
    except OSError as e:
        logging.error("OSError: {0}".format(e))
        sys.exit(1)
    try:
        result_config = get_result_config(parser, config)
    except argparse.ArgumentError:
        logging.error("Config file is not parseable")
        sys.exit(1)
    try:
        main(result_config)
    except:
        logging.exception("Unexpected error")
