class DefaultConfig:
    socketpath = '/var/tmp/crawl_socket'
    agent_name = 'aiagent'
    crawl_socketpath = 'crawl/crawl-ref/source/rcs/' + agent_name + ':test.sock'


class WebserverConfig:
    server_uri = 'ws://127.0.0.1:8080/socket'
    server_ip = '127.0.0.1'
    server_port = '8080'
    agent_name = 'midca'
    agent_password = 'midca'
    game_id = 'dcss-web-trunk'


class CharacterCreationConfig:
    species = 'Minotaur'  # species name must match exactly to the string in the dcss menu after the dash, i.e. a hill orc is "Hill Orc"
    background = "Berserker"  # background name must match exactly to the string in the dcss menu after the dash
    starting_weapon = "hand axe"  # starting_weapon name must match exactly to the string in the dcss menu after the dash


class AIConfig:
    ai_python_class = 'SimpleRLAgent'