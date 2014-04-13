import os

from team_not_found import platform_helper


config = {
    'db': {
        'name': 'tnf',
        'host': '127.0.0.1',
        'port': 5432,
        'user': 'tnfuser',
        'password': 'tnfuser',
    },
    'cherrypy': {
        'host': '127.0.0.1',
        'port': 8080,
        'sock': '/home/tnfuser/team_not_found/dynamic/socks/tnf.{pid}.sock',
        'static_timeout_hours': 0,
    },
    'logging': {
        'log_to_console': True,
        'log_level': 'DEBUG',
        'access_logging_enabled': False,
        'disabled_loggers': [],
        'log_folder': '/home/tnfuser/team_not_found/dynamic/logs/',
        'log_file': 'output.log',
        'log_file_size': 10,
    },
    'team': {
        'folder': '/home/tnfuser/team_not_found/dynamic/teams/'
    },
    'match': {
        'folder': '/home/tnfuser/team_not_found/dynamic/matches/'
    },
    'email': {
        'server': 'smtp.mailserver.com',
        'port': 1234,
        'from_name': 'TeamNotFound',
        'from_email': 'from@email.address',
        'username': 'mail_username',
        'password': 'mail_password',
    },
    'root_url': 'https://yourserver.com/path/to/splash_page/',
    'secret': 'TeamNotFoundIsTotallyAwesome!!1!'
}

if platform_helper.WIN32:
    config['db']['user'] = 'postgres'
    config['db']['password'] = 'postgres'
    config['cherrypy']['sock'] = 'C:/dev/team_not_found/dynamic/socks/tnf.{pid}.sock'
    config['logging']['log_folder'] = 'C:/dev/team_not_found/dynamic/logs/'
    config['team']['folder'] = 'C:/dev/team_not_found/dynamic/teams/'
    config['match']['folder'] = 'C:/dev/team_not_found/dynamic/matches/'

config['cherrypy']['sock'] = config['cherrypy']['sock'].format(
    pid = os.getpid()
)
