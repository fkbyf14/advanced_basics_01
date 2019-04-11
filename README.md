The log_analyzer.py script parses nginx logs in specified directory and
generates report about time used to process requests to different URLs

Files for launch:
- log_analyzer.py
- template report.html
- default config config_root.conf
- nginx-access-ui.log-20170701 

###### Usage example
`<python3 log_analyzer.py --config log_analyzer.conf>`

###### Testing
`<python3 tests.py>`
