class DefaultConfig:
    socketpath = '/var/tmp/crawl_socket'
    agent_name = 'aiagent'
    crawl_socketpath = 'crawl/crawl-ref/source/rcs/' + agent_name + ':test.sock'


class WebserverConfig:
    server_uri = 'ws://localhost:8080/socket'
    agent_name = 'midca'
    agent_password = 'midca'
    game_id = 'dcss-web-trunk'


