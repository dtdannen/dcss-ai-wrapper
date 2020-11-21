

class DefaultConfig:

    socketpath = '/var/tmp/crawl_socket'
    agent_name = 'aiagent'
    crawl_socketpath = 'crawl/crawl-ref/source/rcs/'+agent_name+':test.sock'

    def __init__(self):
        pass


class WebserverConfig:
    socketpath = 'https://localhost:8080'
    agent_name = 'midca'
    crawl_socketpath = 'crawl/crawl-ref/source/rcs/' + agent_name + ':test.sock'

    def __init__(self):
        pass
