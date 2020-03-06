# Run crawl with the following command line
# ./crawl -name midca -rc ./rcs/midca.rc -macro ./rcs/midca.macro -morgue ./rcs/midca -sprint -webtiles-socket ./rcs/midca:test.sock -await-connection

import socket
import json
from datetime import datetime, timedelta
import warnings
import os
import random
import time


#crawl_socketpath = '/Users/Decker/Documents/Repos/crawl/crawl-ref/source/rcs/midca:test.sock'
crawl_socketpath = '/home/dustin/Projects/dcss-ai-wrapper/crawl/crawl-ref/source/rcs/midca:test.sock'


crawl_socket = None


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
        print("Sent data")
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
        print("fragmented data {}".format(msg_buffer))
    else:
        msg_buffer = None
        print("data {}".format(msg_buffer))        
        return data
    return ''


def read_msgs():
    msgs = []
    data = read_msg()
    # TODO: This doesn't seem to be the correct way to determine the end of the messages
    while "flush_messages" not in data:
        if len(data) > 0 and not data.startswith("*"): 
            msgs.append(json.loads(data))
        elif data.startswith("*"): 
            server_msg = json.loads(data[1:])
            # TODO: Handle server messages (client_path,flush_messages,dump,exit_reason)
        data = read_msg()
    return msgs


def send_and_receive(input_str):
    send_input(input_str)
    msgs = read_msgs()
    return msg


if os.path.exists(crawl_socketpath):

    primary = True

    crawl_socket = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
    crawl_socket.settimeout(10)
    print("Set timeout")
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
        #warnings.simplefilter("ignore")
        socketpath = os.tempnam(None, "crawl")

    print("about to bind socket path")
    crawl_socket.bind(socketpath)

    print("about to send msg")
    send_message(msg)
    read_msgs()

    print("Selecting game mode and choosing character configuration...")

    # select sprint and character build
    send_and_receive('a') # choose Sonja spring
    print("send_and_receive('a') # choose Sonja spring")

    send_and_receive('b') # choose Minotaur
    print("send_and_receive('b') # choose Minotaur    ")

    send_and_receive('h') # choose Berserker
    print("send_and_receive('h') # choose Berserker")

    send_and_receive('a') # choose short sword
    print("send_and_receive('a') # choose short sword    ")


    # move some random steps
    print("About to start sending random moves...")
    i = 0
    while i < 20:
        direction = random.choice(dir_map.keys())
        print("  moving {}".format(direction))
        send_and_receive(dir_map[direction])
        i = i + 1
        time.sleep(0.25)
    print("Done sending random moves...")

    # Quit and delete the game
    print("Quitting the game and deleting for fresh start next time...")
    control_input('Q')
    time.sleep(0.25)
    send_input('yes\r')
    time.sleep(0.25)
    send_input('\r')
    time.sleep(0.25)
    send_input('\r')
    time.sleep(0.25)
    send_input('\r')
    close()
else:
    print('%s does not exist' % crawl_socketpath)
