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
import statistics
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
pattern_url = re.compile(r'[/\w.*&=\-%?&/]+(?=\sHTTP)')
pattern_time = re.compile(r'\d+\.\d+$')
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


def parse_log_record(log_line):
    request_time = float(pattern_time.search(log_line).group())
    url = pattern_url.search(log_line).group()
    if not request_time or not url:
        logging.error('Unable to parse line: "{}"'.format(log_line))
        return None

    return url, request_time


def create_or_update_data_of_url(data_of_urls, url, request_time):
    item = data_of_urls.get(url)
    if not item:
        item = {'url': url,
                'requests_count': 0,
                'request_time_sum': 0,
                'max_request_time': request_time,
                'request_time_avg': 0,
                'request_time_all': []}
        data_of_urls[url] = item

    item['requests_count'] += 1
    item['request_time_sum'] += request_time
    item['max_request_time'] = max(item['max_request_time'], request_time)
    item['request_time_avg'] = item['request_time_sum'] / item['requests_count']
    item['request_time_all'].append(request_time)


def final_data_of_url(data_of_urls, item, total_request, total_time):
    url = data_of_urls[item]['url']
    count = data_of_urls[item]['requests_count']
    count_perc = count * 100 / total_request
    time_sum = sum(data_of_urls[item]['request_time_all'])
    time_perc = data_of_urls[item]['request_time_sum'] * 100 / total_time
    time_avg = data_of_urls[item]['request_time_avg']
    time_max = data_of_urls[item]['max_request_time']
    time_med = statistics.median(data_of_urls[item]['request_time_all'])

    return {
        'count': count,                  # сколько раз встречается URL, абсолютное значение
        "time_avg": round(time_avg, 3),  # средний $request_time для данного URL'а
        "time_max": round(time_max, 3),  # максимальный $request_time для данного URL'а
        "time_sum": round(time_sum, 3),  # суммарный $request_time для данного URL'а, абсолютное значение
        "url": url,
        "time_med": round(time_med, 3),  # медиана $request_time для данного URL'а
        "time_perc": round(time_perc, 3), # суммарный $request_time для данного URL'а, в процентах относительно
                                          # общего $request_time всех запросов
        "count_perc": round(count_perc, 3) # сколько раз встречается URL, в процентах относительно общего числа запросов

    }


def count_data(path_last_log, errors_limit=None):
    count_of_fail = 0
    data_of_urls = {}
    total_time = 0
    total_request = 0
    result_table = []
    for log_line in parse_log(path_last_log):
        total_request += 1
        if not parse_log_record(log_line):
            count_of_fail += 1
            continue

        url, request_time = parse_log_record(log_line)
        total_time += request_time
        create_or_update_data_of_url(data_of_urls, url, request_time)

    if total_request != 0 and count_of_fail / total_request > errors_limit:
        logging.info('Level has overrun part_of_fail')
        return

    for item in data_of_urls:
        result_table.append(final_data_of_url(data_of_urls, item, total_request, total_time))

    sorted_res_table = sorted(result_table, key=lambda row: row['time_sum'], reverse=True)
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
    parser.add_argument('--config', help='Config file path', nargs='?',
                        default=DEFAULT_CONFIG_PATH)
    args = parser.parse_args()

    config = load_conf(DEFAULT_CONFIG_PATH)
    if args.config:
        external_config = load_conf(args.config)
        config.update(external_config)

    logging.debug("result config is: {}".format(config))

    try:
        main(config)
    except:
        logging.exception("Unexpected error")
