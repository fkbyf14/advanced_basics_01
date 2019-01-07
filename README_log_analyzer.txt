�����������!

���� ��� ������������ ������ � ���������� path_for_logging, ���������� ��� �����������
��������� � "LOG_DIR" ���������� �������.
��� ������� � ������������ ��������� ���������� ��������� �����:
- log_analyzer.py
- test_log_analyzer.py
- ������ report.html
����� ��������:
- config_root.txt  - ��������� ������
- user_config.txt  - � ���� ��������� ���� ����� --config
- user_config_empty.txt - � ���� ��������� ���� ����� --config
����� �����:
1 nginx-access-ui.log-20170308
2 nginx-access-ui.log-20170630.gz
3 nginx-access-ui.log-20170701  //small
4 nginx-access-ui.log-20170430.txt
5 another-service-ui.log-20170301
6 nginx-access-ui.log-20170630
7 nginx-access-ui.log-20170730  //ansi with blank lines and strange line
*************************************************************************************************
������ �������.
1. ������ ������� �� ��������� ������ ��� ���������, ����������� ����� --config:
����������� ��������� ���� �������, ���������� � ���������� default_config_path.
�� ����� ���� ����� ���� config_root.txt.
� LOG_DIR ���������� ���� � 1 �� 5, � �������� �������� ������ 1. 
����� ����� ����� � ... ��� ������ report-2017.03.08_launch1.

2. ������ ������� �� ��������� ������ � ����������, ���������� ����� --config: ������� ���� � �����
user_config.txt. � LOG_DIR ���������� ���� �� 2 �� 5, � �������� �������� ������ 
nginx-access-ui.log-20170630.gz. ���������� ����� - report-2017.06.30_launch2.


3. ������ ������� �� ��������� ������ � ����������, ���������� ����� --config: ������� ���� � 
������� ����� user_config_empty.txt.: ����������� ��������� ������, ���������� � ���������� config:
config = {
    "REPORT_SIZE": 10,
    "REPORT_DIR": r"C:\Users\user\reports",
    "LOG_DIR": r"C:\Users\user\log"
}
- � LOG_DIR ���������� ���� �� 2 �� 6, � �������� �������� ������ nginx-access-ui.log-20170630.
���������� ����� - report-2017.06.30_launch3.1.
- ����������, "REPORT_SIZE": 20, � LOG_DIR ���������� ��� ��� ������� 7, ���� �� ����� �������� �� ������ �������:
"� �������". 
���������� ��� - logging_launch3.2: UnicodeDecodeError.
-------------------------------------------------------------------------------------------------
�������� �������.
1. test_create_parser �� ����� ������ ������, ����������� ���, ������������ ��������
2. test_get_result_config - ��������� �������� ��� ��������� ������� �������, ������������� �����
--config
3. test_search_last_log �� ������ ������ (�����), ��������������� 1�� ������� �����.
4. test_count_data c ����� �3 (small)

------------------------------------------------------------------------------------------------
[help]
��������� � ������, � �� ���� ������� ����������� ������ argparse ��� ��������������� error ��� ����.
�� ������� ����:
 except FileNotFoundError as e:
            logging.error("OSError: {0}".format(e))
            sys.exit(1)
        try:
            result_config = get_result_config(parser, config)
        except argparse.ArgumentError:
            logging.error("Config file is not parseable")
            sys.exit(1)

�����, ������� ������� ���� � ��������:
def get_result_config(parser, default_config):
    args = parser.parse_args()
    with args.config as path_config:
        text_config = path_config.read()
��, �������, �� ���������. ����� �������: ResourceWarning: unclosed file. �� �������, ������
������� ����������� � ������ warnings.filterwarnings('ignore', category=ResourceWarning) �� ��������.
� ���� ����� ���-�� �� ���.
���������� ����������, ��� ����� ���������� ������� ��� ����� ���������.