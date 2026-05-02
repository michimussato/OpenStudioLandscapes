import os
import pathlib
from typing import Dict

LOG_ROOT: pathlib.Path = pathlib.Path("~/.config/OpenStudioLandscapes/logs").expanduser()
LOG_ROOT.mkdir(parents=True, exist_ok=True)


# Resources:
# - [A Complete Guide to Linux Log File Locations and Their Usage](https://last9.io/blog/linux-log-file-locations/)
# - [Mastering Python Logging: A Guide to dictConfig() Troubleshooting and Alternatives](https://runebook.dev/en/docs/python/library/logging.config/logging.config.dictConfig)
# - [](https://stackoverflow.com/questions/7507825/where-is-a-complete-example-of-logging-config-dictconfig)
#
# Follow logs:
# - [](https://unix.stackexchange.com/a/687072/535903)


LOGGING_SCHEMA: Dict = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            'format': '[{asctime}] [{levelname:<8}] [{threadName}|{thread}], File "{pathname}", line {lineno}, in {funcName}:    {message}',
            'style': '{',
            'datefmt': '%m-%d-%Y %H:%M:%S',
        },
    },
    'handlers': {
        'console': {
            'level': 'WARNING',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'cli_filehandler': {
            'level': 'DEBUG',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'when': 'midnight',
            'interval': 1,
            'backupCount': 7,
            'filename': os.path.join(LOG_ROOT, 'cli.log'),
            'formatter': 'simple',
        },
        'discovery_filehandler': {
            'level': 'DEBUG',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'when': 'midnight',
            'interval': 1,
            'backupCount': 7,
            'filename': os.path.join(LOG_ROOT, 'discovery.log'),
            'formatter': 'simple',
        },
        'engine_filehandler': {
            'level': 'DEBUG',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'when': 'midnight',
            'interval': 1,
            'backupCount': 7,
            'filename': os.path.join(LOG_ROOT, 'engine.log'),
            'formatter': 'simple',
        },
        'features_filehandler': {
            'level': 'DEBUG',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'when': 'midnight',
            'interval': 1,
            'backupCount': 7,
            'filename': os.path.join(LOG_ROOT, 'features.log'),
            'formatter': 'simple',
        },
    },
    'loggers': {
        'OpenStudioLandscapes.cli': {
            'handlers': ['console', 'cli_filehandler'],
            'propagate': False,
            # 'level': 'WARNING',
        },
        'OpenStudioLandscapes.discovery': {
            'handlers': ['console', 'discovery_filehandler'],
            'propagate': False,
            # 'level': 'WARNING',
        },
        # 'OpenStudioLandscapes.engine.utils': {
        #     'handlers': ['console', 'utils_filehandler'],
        #     'propagate': False,
        #     'level': 'WARNING',
        # },
        # 'OpenStudioLandscapes.engine.common_assets': {
        #     'handlers': ['console', 'utils_filehandler'],
        #     'propagate': False,
        #     'level': 'WARNING',
        # },
        # 'OpenStudioLandscapes.engine.compose_scopes': {
        #     'handlers': ['console', 'compose_scopes_filehandler'],
        #     'propagate': False,
        #     'level': 'WARNING',
        # },
        'OpenStudioLandscapes.engine': {
            'handlers': ['console', 'engine_filehandler'],
            'propagate': False,
            # 'level': 'WARNING',
        },
        'OpenStudioLandscapes.Features': {
            'handlers': ['console', 'features_filehandler'],
            'propagate': False,
            # 'level': 'WARNING',
        },
        # 'urllib3': {
        #     'handlers': ['console', 'file'],
        #     # 'propagate': True,
        #     'level': 'WARNING',
        # },
        # 'selenium': {
        #     'handlers': ['console', 'file'],
        #     # 'propagate': True,
        #     'level': 'WARNING',
        # },
        # 'asyncio': {
        #     'handlers': ['console', 'file'],
        #     # 'propagate': True,
        #     'level': 'WARNING',
        # },
        # 'omxplayer': {
        #     'handlers': ['console', 'file'],
        #     # 'propagate': True,
        #     'level': 'WARNING',
        # },
    },
    'root': {
        'level': 'DEBUG',
        'handlers': ['console']
    }
}
