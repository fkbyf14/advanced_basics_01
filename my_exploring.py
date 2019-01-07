import json
import re
import os
from datetime import datetime
from string import Template
import logging
import argparse
import ast
import sys

config = {
    "REPORT_SIZE": 1000,
    "REPORT_DIR": "./reports",
    "LOG_DIR": r"C:\Users\user\logs"
}

text_2 = r'1.99.174.176 3b81f63526fa8  - [29/Jun/2017:03:50:22 +0300] "GET /api/1/photogenic_banners/list/?server_name=WIN7RB4 HTTP/1.1" 200 12 "-" "Python-urllib/2.7" "-" "1498697422-32900793-4708-9752770" "-" 0.133'
text_1 = r'1.196.116.32 -  - [29/Jun/2017:03:50:22 +0300] "GET /api/v2/banner/25019354 HTTP/1.1" 200 927 "-" "Lynx/2.8.8dev.9 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/2.10.5" "-" "1498697422-2190034393-4708-9752759" "dc7161be3" 0.390'
text = r'1.196.116.32 -  - [29/Jun/2017:03:50:22 +0300] "GET /agency/outgoings_stats/?date1=29-06-2017&date2=29-06-2017&date_type=day&do=1&rt=banner&oi=24123738&as_json=1 HTTP/1.1" 200 927 "-" "Lynx/2.8.8dev.9 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/2.10.5" "-" "1498697422-2190034393-4708-9752759" "dc7161be3" 0.390'

logging.basicConfig(format='[%(asctime)s] %(levelname).1s %(message)s', level=logging.DEBUG)
"""
# Сообщение отладочное
logging.debug(u'This is a debug message')
# Сообщение информационное
logging.info(u'This is an info message')
# Сообщение предупреждение
logging.warning(u'This is a warning')
# Сообщение ошибки
logging.error(u'This is an error message')
# Сообщение критическое
logging.critical(u'FATAL!!!')
"""


def create_parser():
    try:
        parser = argparse.ArgumentParser()

        parser.add_argument('--config', nargs='?', type=argparse.FileType(),
                            default=r'C:\Users\user\PycharmProjects\advanced_basics_01\config_root.txt')
        #print(type(parser))
        return parser
    except EnvironmentError:
        #print("OSError: {0}".format(e))
        print('toup')


parser_ = create_parser()
config_path = parser_.parse_args()
text_config = config_path.config.read()
if isinstance(parser_, argparse.ArgumentParser):
    print(True)




