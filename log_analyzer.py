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
from collections import Counter
import logging

config = {
    "REPORT_SIZE": 20,
    "REPORT_DIR": r"C:\Users\user\reports",
    "LOG_DIR": r"C:\Users\user\log\small"
}


def search_last_log(log_dir):
    """ Ищет свежий лог сервиса nginx-access-ui в формате plain или gzip"""
    named_tuple = tuple()
    try:
        names = os.listdir(log_dir)
        date_pattern = re.compile('\d{8}')
        dict_logs = {}
        for name in names:
            if name.startswith('nginx-access-ui.log-'):
                fullname = os.path.join(log_dir, name)
                date_string = date_pattern.search(name).group()
                date = datetime.strptime(date_string, "%Y%m%d")
                path, ext = os.path.splitext(fullname)
                if ext == '.log-' + date_string or ext == '.gz':
                    dict_logs[date] = fullname
                    min_date = min(dict_logs.keys())
                    named_tuple = dict_logs[min_date], min_date.strftime("%Y.%m.%d")
                    logging.info("Log "+str(named_tuple)+" has chosen")
                    return named_tuple
        logging.info("I can't find appropriate log of nginx-access-ui service")
        return named_tuple
    except OSError as err:
        logging.error("OS error: {0}".format(err))
        print("OS error: {0}".format(err))
        return named_tuple


def parse_log(path_last_log):
    """функция-генератор, открывает файл лога и считывает построчно"""
    path, ext = os.path.splitext(path_last_log)
    try:
        with gzip.open(path_last_log, 'rt', encoding='UTF-8') if ext == '.gz' \
                else open(path_last_log, 'rt', encoding='UTF-8') as f:
            for line in f.readlines():
                yield line
    except OSError as e:
        print("OSError: {0}".format(e))
        logging.error("OSError: {0}".format(e))


def count_data(path_last_log):
    """считает необходимые данные:
    count ‑ сколько раз встречается URL, абсолютное значение
    count_perc ‑ сколько раз встречается URL, в процентнах относительно общего числа запросов
    time_sum ‑ суммарный $request_time для данного URL'а, абсолютное значение
    time_perc ‑ суммарный $request_time для данного URL'а, в процентах относительно общего $request_time всех
    запросов
    time_avg ‑ средний $request_time для данного URL'а
    time_max ‑ максимальный $request_time для данного URL'а
    time_med ‑ медиана $request_time для данного URL'а"""
    pattern_url = re.compile('[/\w.*&=\-%?&/]+(?=\sHTTP)')
    pattern_time = re.compile('\d+\.\d+$')
    count_of_fail = 0
    list_of_urls = []
    data_of_urls = {}
    request_time_all = 0
    number_of_request = 0
    res_table = []
    part_of_fail = 0.5
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
        print("TypeError: {0}".format(e))
        logging.error("TypeError: {0}".format(e))
    if number_of_request != 0 and count_of_fail / number_of_request > part_of_fail:
        logging.info('Level has overrun part_of_fail')
        return []
    for row in res_table:
        row['time_perc'] = round(row['time_sum'] * 100 / request_time_all, 3)
        row['count_perc'] = round(row['count'] * 100 / number_of_request, 3)
    sorted_res_table = sorted(res_table, key=lambda row: row['time_sum'], reverse=True)
    logging.info(str(sorted_res_table))
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
        if text_config != '':
            config_param = re.split('= ', text_config)
            config_from_file = dict(ast.literal_eval(config_param[1]))
            result_config = default_config.copy()
            result_config.update(config_from_file)
            logging.info("Result config = merge of config from file and default")
        else:
            result_config = default_config.copy()
            logging.info("Config from file is empty, I've taken default")
            logging.debug("result config is:" + str(result_config))
        return result_config


def main():
    try:
        path_for_logging = config["LOG_DIR"] + r'\logging.txt'
        if "LOG_DIR" in config:
            logging.basicConfig(format='[%(asctime)s] %(levelname).1s %(message)s', level=logging.DEBUG,
                                filename=path_for_logging)
        else:
            logging.basicConfig(format='[%(asctime)s] %(levelname).1s %(message)s', level=logging.DEBUG,
                                filename=None)
        default_config_path = r'C:\Users\user\PycharmProjects\advanced_basics_01\config_root.txt'
        if not os.path.isfile(default_config_path):
            logging.info('default_config_path is not available')
        try:
            parser = create_parser(default_config_path)
        except FileNotFoundError as e:
            logging.error("OSError: {0}".format(e))
            sys.exit(1)
        try:
            result_config = get_result_config(parser, config)
        except argparse.ArgumentError:
            logging.error("Config file is not parseable")
            sys.exit(1)
        search_tuple = search_last_log(result_config["LOG_DIR"])
        if search_tuple:
            names = os.listdir(result_config["REPORT_DIR"])
            if 'report-' + search_tuple[1] + '.html' in names:
                logging.info('Work has already been done')
                sys.exit(0)
            res_table = count_data(search_tuple[0])
            if res_table:
                report_path = os.path.join(result_config['REPORT_DIR'], 'report-' + search_tuple[1] + '.html')
                render_template(res_table[:result_config["REPORT_SIZE"]], report_path)
            else:
                logging.error('Data not counted')
                sys.exit(0)
        else:
            logging.error('Last log not available')
            sys.exit(0)
    except BaseException:
        print("Unexpected error:", sys.exc_info()[0])
        logging.exception("Unexpected error")


if __name__ == "__main__":
    main()
