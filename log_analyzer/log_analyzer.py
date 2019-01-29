#!/usr/bin/env python
# -*- coding: utf-8 -*-


# log_format ui_short '$remote_addr  $remote_user $http_x_real_ip [$time_local] "$request" '
#                     '$status $body_bytes_sent "$http_referer" '
#                     '"$http_user_agent" "$http_x_forwarded_for" "$http_X_REQUEST_ID" "$http_X_RB_USER" '
#                     '$request_time';
import json
import re
import os
import gzip
from datetime import datetime
from string import Template
from functools import reduce
import argparse
from collections import Counter, namedtuple
import logging

""" Пример конфига """
"""{"REPORT_SIZE": 100,
    "REPORT_DIR": "./",
    "LOG_DIR": "./log",
    "LOGGING": "./logging.log",
    "ERRORS LIMIT": 0.5}"""

DEFAULT_CONFIG_PATH = "./config_root.conf"
LastLogInfo = namedtuple('Log', ['path', 'date'])


def load_conf(conf_path):
    with open(conf_path, 'rb') as conf_file:
        conf = json.load(conf_file, encoding='UTF-8')
    return conf


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


def main(config):
    if not os.path.isdir(os.path.dirname(config["LOGGING"])):
        os.makedirs(os.path.dirname(config["LOGGING"]))
    logging.basicConfig(format='[%(asctime)s] %(levelname).1s %(message)s', level=logging.DEBUG,
                        filename=config["LOGGING"])

    the_latest_log_info = search_last_log(config["LOG_DIR"])
    if not the_latest_log_info:
        logging.info('No log files yet')
        return

    report_date = the_latest_log_info.date.strftime("%Y.%m.%d")
    report_filename = 'report-{}.html'.format(report_date)
    report_file_path = os.path.join(config["REPORT_DIR"], report_filename)

    if os.path.isfile(report_file_path):
        logging.info('Work has already been done')
        return

    result_data_table = count_data(the_latest_log_info.path, config["ERRORS LIMIT"])
    if not result_data_table:
        logging.error('Data not counted')
        return

    render_template(result_data_table[:config["REPORT_SIZE"]], report_file_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', help='Config file path', nargs='?', type=argparse.FileType('r'),
                        default=DEFAULT_CONFIG_PATH)
    args = parser.parse_args()

    config = load_conf(DEFAULT_CONFIG_PATH)
    if args.config:
        external_config = load_conf(args.config.name)
        config.update(external_config)

    logging.debug("result config is: {}".format(config))

    try:
        main(config)
    except:
        logging.exception("Unexpected error")
