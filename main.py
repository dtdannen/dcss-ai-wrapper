"""

Demo of an RL agent on the sonja sprint in crawl 23.1

Make sure to run crawl before running this demo, see:
    start_crawl_terminal_sprint.sh

"""

import socket
import json
from datetime import datetime, timedelta
import warnings
import os
import random
from gamestate import GameState
import logging
import time
import sys

logging.basicConfig(level=logging.DEBUG)

crawl_socket = None
game_state = GameState()

dir_map = { 'NW' : 'y',  'N' : 'k', 'NE' : 'u',
             'W' : 'h',              'E' : 'l',
            'SW' : 'b',  'S' : 'j', 'SE' : 'n' }

def json_encode(value):
    return json.dumps(value).replace("</", "<\\/")

def close():
    global crawl_socket
    if crawl_socket:
        print ("Closing socket...")
        crawl_socket.close()
        #socketpathobj.close()
        os.unlink(socketpath)
        crawl_socket = None

def send_message(data):
    start = datetime.now()
    try:
        crawl_socket.sendto(data.encode('utf-8'), crawl_socketpath)
    except socket.timeout:
        #self.logger.warning("Game socket send timeout", exc_info=True)
        print("ERROR: in send_message() - Game socket send timeout")
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

num_times_to_try_pressing_enter = 5
num_times_pressed_enter = 0

msg_buffer = None
def read_msg():
    global msg_buffer
    global num_times_pressed_enter
    try:
        data = crawl_socket.recv(128 * 1024, socket.MSG_DONTWAIT)
        num_times_pressed_enter = 0
    except socket.timeout:
        # first try to send and receive 'r' since the game might just be waiting with lots of messages
        if num_times_pressed_enter <= num_times_to_try_pressing_enter:
            send_and_receive('\r')
            num_times_pressed_enter+=1
        else:
            print("ERROR: in read_msg() - Game socket send timeout")
            close()
            return ''

    if isinstance(data,bytes):
        data = data.decode("utf-8") 

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

def handle_msgs(msgs):   
    game_state.update(msgs)

def read_msgs():
    msgs = []
    data = read_msg()
    # TODO: This doesn't seem to be the correct way to determine the end of the messages
    while "flush_messages" not in data:
        if len(data) > 0 and not data.startswith("*"): 
            msgs.append(json.loads(data))
            #game_state.update(msgs[-1])
        elif data.startswith("*"): 
            server_msg = json.loads(data[1:])
            # TODO: Handle server messages (client_path,flush_messages,dump,exit_reason)
        data = read_msg()
    handle_msgs(msgs)

def send_and_receive(input_str):
    logging.debug("Sending {}".format(input_str))
    send_input(input_str)
    msgs = read_msgs()
    handle_msgs(msgs)

#crawl_socketpath = '/home/dustin/Projects/dcss-ai-wrapper/crawl/crawl-ref/source/rcs/midca:test.sock'
crawl_socketpath = '/home/dustin/crawl/crawl-ref/source/rcs/midca:test.sock'
socketpath = '/var/tmp/crawl_socket'

try:
    os.unlink(socketpath)
except OSError:
    if os.path.exists(socketpath):
        raise

HUMAN_INPUT = False
if len(sys.argv) >= 2:
    if 'human' in sys.argv[1]:
        HUMAN_INPUT = True

if os.path.exists(crawl_socketpath) and not os.path.exists(socketpath):

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

    crawl_socket.bind(socketpath)

    send_message(msg)

    read_msgs()

    # This will get all the state from the game at once
    # Parsing error with json library
    # msg = json_encode({
    #         "msg": "spectator_joined"
    #         })
    #send_message(msg)

    def do_sprint():
        # select sprint and character build
        send_and_receive('a')
        send_and_receive('b')
        send_and_receive('h')
        send_and_receive('b')

    def do_dungeon():
        # select sprint and character build
        send_and_receive('b')
        send_and_receive('h')
        send_and_receive('b')

    #do_sprint()
    do_dungeon()

    # turn off auto pick-up
    control_input('A')
    read_msgs()

    # # Get Stone
    # send_and_receive(dir_map['NW'])
    # send_and_receive('g')

    # move some random steps but don't walk into walls
    i = 0
    while( i < 5000 ):
        action_str = "Action %3d - " % (i+1)

        if HUMAN_INPUT:
            human_pressed_key = input('Your Next Action')
            if human_pressed_key == "":
                human_pressed_key = '\r'
            send_and_receive(human_pressed_key)
        else:
            direction = random.choice(list(dir_map.keys()))
            send_and_receive(dir_map[direction])
            # if game_state.can_move_direction(direction):
            #     action_str += " Moving %s..." % direction
            #     send_and_receive(dir_map[direction])
            # elif game_state.can_open_door(direction):
            #     action_str += " Opening %s door..." % direction
            #     send_and_receive(dir_map[direction])
            # elif game_state.can_attack_monster(direction):
            #     action_str += " Attacking monster %s..." % direction
            #     send_and_receive(dir_map[direction])
            # else:
            #     continue

            if game_state.agent_just_leveled_up():
                print("Woohooo we leveled up!!!!!!!!")
                send_input('\r')

            if game_state.is_agent_too_terrified():
                print("FIX ME")
                time.sleep(10)

            if game_state.agent_cannot_move():
                print("FIX ME")
                time.sleep(10)

            if game_state.has_agent_died():
                print("******* AW MAN ... WE DIED ***********")
                time.sleep(1)
                send_input('\r')
                time.sleep(1)
                send_input('\r')
                time.sleep(1)
                send_input('\r')
                break

            if game_state.game_has_more_messages(reset=True):
                print("more prompt!")
                send_and_receive('\r')

        #time.sleep(1)
        game_state.draw_cell_map()
        print("------------printing raduis of 8 around agent------------")
        game_state.cellmap.print_radius_around_agent(r=8)
        print("Player's current position is {},{}".format(game_state.agent_x, game_state.agent_y))
        #print("Tiles around agent are: {}".format(game_state.get_tiles_around_player_radius()))
        game_state.print_inventory()
        
        i = i + 1
        print(action_str)

    if not game_state.has_agent_died():
        # Quit and delete the game
        control_input('Q')
        time.sleep(1)
        send_input('yes\r')
        time.sleep(1)
        send_input('\r')
        time.sleep(1)
        send_input('\r')
        time.sleep(1)
        send_input('\r')

    close()

    #print("Map Boundaries : %s" % str(game_state.map_obj.get_bounds()))
else:
    print('%s does not exist' % crawl_socketpath)
