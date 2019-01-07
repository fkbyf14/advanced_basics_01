Приветствую!

Путь для логгирования указан в переменной path_for_logging, директория для логирования
совпадает с "LOG_DIR" дефолтного конфига.
Для запуска и тестирования программы необходимы следующие файлы:
- log_analyzer.py
- test_log_analyzer.py
- шаблон report.html
Файлы конфигов:
- config_root.txt  - дефолтный конфиг
- user_config.txt  - к нему указываем путь через --config
- user_config_empty.txt - к нему указываем путь через --config
Файлы логов:
1 nginx-access-ui.log-20170308
2 nginx-access-ui.log-20170630.gz
3 nginx-access-ui.log-20170701  //small
4 nginx-access-ui.log-20170430.txt
5 another-service-ui.log-20170301
6 nginx-access-ui.log-20170630
7 nginx-access-ui.log-20170730  //ansi with blank lines and strange line
*************************************************************************************************
Боевые запуски.
1. Запуск скрипта из командной строки без параметра, переданного через --config:
Применяется дефолтный путь конфига, записанный в переменную default_config_path.
По этому пути лежит файл config_root.txt.
В LOG_DIR содержатся логи с 1 по 5, в качестве рабочего выбран 1. 
Отчет можно найти в ... под именем report-2017.03.08_launch1.

2. Запуск скрипта из командной строки с параметром, переданным через --config: передаём путь к файлу
user_config.txt. В LOG_DIR содержатся логи со 2 по 5, в качестве рабочего выбран 
nginx-access-ui.log-20170630.gz. Полученный отчет - report-2017.06.30_launch2.


3. Запуск скрипта из командной строки с параметром, переданным через --config: передаём путь к 
пустому файлу user_config_empty.txt.: применяется дефолтный конфиг, записанный в переменной config:
config = {
    "REPORT_SIZE": 10,
    "REPORT_DIR": r"C:\Users\user\reports",
    "LOG_DIR": r"C:\Users\user\log"
}
- В LOG_DIR содержатся логи со 2 по 6, в качестве рабочего выбран nginx-access-ui.log-20170630.
Полученный отчет - report-2017.06.30_launch3.1.
- Аналогично, "REPORT_SIZE": 20, в LOG_DIR содержится лог под номером 7, одна из строк сообщает на чистом русском:
"я чудачок". 
Полученный лог - logging_launch3.2: UnicodeDecodeError.
-------------------------------------------------------------------------------------------------
Тестовые запуски.
1. test_create_parser на любом наборе данных, проверяется тип, возвращаемый функцией
2. test_get_result_config - несколько проверок при различной полноте конфига, передаваемого через
--config
3. test_search_last_log на наборе данных (логов), соответствующих 1му боевому тесту.
4. test_count_data c логом №3 (small)

------------------------------------------------------------------------------------------------
[help]
Насколько я поняла, я не могу вручную перехватить ошибки argparse без переопределения error для него.
Но попытки есть:
 except FileNotFoundError as e:
            logging.error("OSError: {0}".format(e))
            sys.exit(1)
        try:
            result_config = get_result_config(parser, config)
        except argparse.ArgumentError:
            logging.error("Config file is not parseable")
            sys.exit(1)

Также, попытка закрыть файл с конфигом:
def get_result_config(parser, default_config):
    args = parser.parse_args()
    with args.config as path_config:
        text_config = path_config.read()
Но, кажется, не сработало. Тесты говорят: ResourceWarning: unclosed file. Не понимаю, почему
попытка перехватить в тестах warnings.filterwarnings('ignore', category=ResourceWarning) не работает.
Я явно делаю что-то не так.
Подскажите пожалуйста, как можно попытаться сделать это более правильно.