# Run crawl with the following command line
# ./crawl -name midca -rc ./rcs/midca.rc -macro ./rcs/midca.macro -morgue ./rcs/midca -sprint -webtiles-socket ./rcs/midca:test.sock -await-connection

import socket
import json
from datetime import datetime, timedelta
import warnings
import os
import random
import time
import json_to_predicate_calculus
#from dcss_gamestate import GameState

LOG_FILE_NAME = "server_msgs_full_game_log_"+datetime.fromtimestamp(time.time()).strftime('%m-%d-%H-%M-%S')
LOG_FILE = open(LOG_FILE_NAME, 'w')

crawl_socket = None
#game_state = GameState()

dir_map = { 'NW' : 'y',  'N' : 'k', 'NE' : 'u',
             'W' : 'h',              'E' : 'l',
            'SW' : 'b',  'S' : 'j', 'SE' : 'n' }


def json_encode(value):
    return json.dumps(value).replace("</", "<\\/")

def close():
    global crawl_socket
    if crawl_socket:
        crawl_socket.close()
        #socketpathobj.close()
        os.remove(socketpath)
        crawl_socket = None

def send_message(data):
    start = datetime.now()
    try:
        crawl_socket.sendto(data.encode('utf-8'), crawl_socketpath)
    except socket.timeout:
        #self.logger.warning("Game socket send timeout", exc_info=True)
        print("Game socket send timeout")
        close()
        return
    end = datetime.now()
    if end - start >= timedelta(seconds=1):
        print("Slow socket send: " + str(end - start))
        #self.logger.warning("Slow socket send: " + str(end - start))


def control_input(c):
    send_message(json_encode({'msg':'key', 'keycode':ord(c)-ord('A')+1}))

def send_input(input_str):
    for c in input_str:
        send_message(json_encode({'msg':'key', 'keycode':ord(c)}))

msg_buffer = None
def read_msg():
    global msg_buffer
    data = crawl_socket.recv(128 * 1024, socket.MSG_DONTWAIT)
    if msg_buffer is not None:
        data = msg_buffer + data
    if data[-1] != "\n":
        # All messages from crawl end with \n.
        # If this one doesn't, it's fragmented.
        msg_buffer = data
    else:
        msg_buffer = None
        return data
    return ''

def read_msgs():
    msgs = []
    data = read_msg()
    # TODO: This doesn't seem to be the correct way to determine the end of the messages
    msg_i = 0
    while "flush_messages" not in data:
        if len(data) > 0 and not data.startswith("*"): 
            msgs.append(json.loads(data))
            #game_state.update(msgs[-1])
        elif data.startswith("*"): 
            server_msg = json.loads(data[1:])
            # TODO: Handle server messages (client_path,flush_messages,dump,exit_reason)
        data = read_msg()
        LOG_FILE.write(str(msg_i)+": "+data)
        msg_i+=1

    # TODO: temp code to see what I'm working with
    for m in msgs:
        i = 0
        facts = json_to_predicate_calculus.parse_message(m)
        end = len(facts)
        while i < end:
            if i + 1 <= end:
                print("{:50s} | {:50s}".format(facts[i], facts[i + 1]))
                i += 2
            else:
                print("{:50s}".format(facts[i]))
                i += 1

    return msgs

def send_and_receive(input_str):
    send_input(input_str)
    msgs = read_msgs()
    return msg

#crawl_socketpath = '/Users/Decker/Documents/Repos/crawl/crawl-ref/source/rcs/midca:test.sock'
crawl_socketpath = '/home/dustin/dcss_api/crawl/crawl-ref/source/rcs/midca:test.sock'

if os.path.exists(crawl_socketpath):

    primary = True

    crawl_socket = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
    crawl_socket.settimeout(10)

    crawl_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    if (crawl_socket.getsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF) < 2048):
        crawl_socket.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 2048)

    if (crawl_socket.getsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF) < 212992):
        crawl_socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 212992)

    msg = json_encode({
            "msg": "attach",
            "primary": primary
            })

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        #socketpathobj = tempfile.NamedTemporaryFile(prefix="crawl")
        socketpath = os.tempnam(None, "crawl")
        # socketpath = "/var/tmp/crawlHW9O3N" # TODO: Replace this fixed path
    
    #socketpath = server_path

    crawl_socket.bind(socketpath)
    #crawl_socket.bind(socketpathobj.name)

    send_message(msg)
    read_msgs()

    while(True):
        in_str = raw_input("Next move please: ")
        if in_str == 'quit':
            break
        else:
            try:
                send_and_receive(in_str)
            except:
                control_input(in_str)

            LOG_FILE.write("\n|*|*|*| Just Sent Action: "+in_str+" |*|*|*|\n")

    close()
else:
    print('%s does not exist' % crawl_socketpath)
