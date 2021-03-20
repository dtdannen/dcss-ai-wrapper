"""

Demo of an agent connecting and playing to a webserver

"""
import asyncio
import websockets
import zlib
import json
import time
import logging
import sys
import threading
import signal
import datetime
import functools
import signal
import os
import pprint
from game_connection import GameConnection
from agent import SimpleRandomAgent, TestAllCommandsAgent, FastDownwardPlanningAgent
from actions import Command, Action

server_uri = 'ws://localhost:8080/socket'

### CHANGE USERNAME AND PASSWORD HERE ###
login_msg = {'msg': 'login',
             'username': 'midca',
             'password': 'midca'}

decomp = zlib.decompressobj(-zlib.MAX_WBITS)


class WebTilesConnection():
    last_msg_from_server = {}

    def __init__(self, ai=None):
        self.websocket = None
        self.logged_in = False
        self.ai = ai
        self.recv_counter = 0
        self.CREATE_NEW_GAME = False
        self.game_ended = False
        self.begin_shutdown = False

    def pretty_print_server_msg(self, msg_from_server):
        try:
            for msg in msg_from_server['msgs']:
                print("--> New Message from Server <--")
                # ignore_list = ['cell','html','content','skip']
                ignore_list = []
                skip_bc_ignore = False
                for key in msg.keys():
                    for ignore in ignore_list:
                        if ignore in key:
                            skip_bc_ignore = True

                    if skip_bc_ignore:
                        skip_bc_ignore = False
                    else:
                        if key == 'cell':
                            for i in msg[key]:
                                print("    " + str(i))
                        else:
                            print(str(key) + ":" + str(msg[key]))

        except Exception as e:
            print("Ignoring unparseable JSON (error: %s): %s.", e.args[0], msg_from_server)

    async def get_all_server_messages(self):
        i = 0
        SERVER_READY_FOR_INPUT = False
        request_pong = False
        while not SERVER_READY_FOR_INPUT:
            try:
                future = self.websocket.recv()
                # print("** AWAITING ON WEBSOCKET RECV in loop, i=" + str(i))
                data_recv = await asyncio.wait_for(future, timeout=0.5)

                # print("** POST-AWAITING ON WEBSOCKET RECV in loop, i=" + str(i))

                data_recv += bytes([0, 0, 255, 255])
                json_message = decomp.decompress(data_recv)
                json_message = json_message.decode("utf-8")

                msg_from_server = json.loads(json_message)

                if 'msgs' in msg_from_server:
                    for msg in msg_from_server['msgs']:
                        if 'msg' in msg:
                            if msg['msg'] == "ping":
                                request_pong = True

                # json_messages_from_server_file.write(pprint.pformat(msg_from_server,indent=2)+'\n')
                # json_messages_from_server_file.flush()

                logging.debug("i=" + str(i) + "Received Message:\n" + str(msg_from_server))

                if self.ai:
                    self.ai.add_server_message(msg_from_server)

                # {'msgs': [{'mode': 1, 'msg': 'input_mode'}]}
                # if 'msgs' in msg_from_server.keys():
                #     for msg in msg_from_server['msgs']:
                #         if 'msg' in msg.keys() and 'mode' in msg.keys():
                #             if msg['msg'] == 'input_mode' and msg['mode'] == 1:
                #                 SERVER_READY_FOR_INPUT = True
                #                 print("Server is now ready for input!")

            except ValueError as e:
                logging.warning("i=" + str(i) + "Ignoring unparseable JSON (error: %s): %s.", e.args[0], json_message)
            except asyncio.CancelledError:
                logging.info('Received message to cancel - ignoring so recv can finish up')
                self.begin_shutdown = True
            except asyncio.TimeoutError:
                # server is now ready for input
                SERVER_READY_FOR_INPUT = True
            # except Exception as e:
            #    logging.warning("Caught exception {} in get_all_server_messages()".format(e))
            i += 1

        if request_pong:
            await self.websocket.send(json.dumps({"msg": "pong"}))

    async def send_and_receive(self, message):
        # send data to server
        # print("AWAITING ON WEBSOCKET_1 SEND - sending message: "+str(message))
        await self.websocket.send(json.dumps(message))
        # print("POST-AWAITING ON WEBSOCKET_1 SEND")
        # wait for server to get back

        await self.get_all_server_messages()

    async def end_session_and_quit_game(self):
        '''
        Sends the ctrl-q signal to the webserver to permamently end the game.
        :return:
        '''
        if not self.game_ended:
            for quit_msg in quit_messages_sequence:
                await self.send_and_receive(quit_msg)

            self.game_ended = True

        logging.info("Sent all quit messages, game is deleted...")

    async def run(self, sprint_id=None):
        # connect
        logging.debug("Connecting to URI " + str(server_uri) + " ...")
        # print("AWAITING ON WEBSOCKET_3 CONNECT")
        self.websocket = await websockets.connect(server_uri)
        # print("POST-AWAITING ON WEBSOCKET_3 CONNECT")
        logging.info("Connected to webserver:" + str(self.websocket and self.websocket.open))

        # login
        logging.debug("Sending login message...")

        await self.send_and_receive(login_msg)

        # break apart msg from server
        # msgs = []
        # if 'msgs' in msg_from_server.keys():
        #    msgs = msg_from_server['msgs']

        logging.debug("Sending pong")

        # send pong
        # for msg_i in msgs:
        #    if msg_i['msg'] == 'ping':
        #        logging.debug("Received message ping from server, about to send pong")
        await self.websocket.send(json.dumps({'msg': 'pong'}))

        logging.debug("Sleeping for 3 seconds")
        time.sleep(3)

        # choose the game mode
        game_id = 'sprint-web-trunk'
        play_game_msg = {'msg': 'play', 'game_id': game_id}
        await self.send_and_receive(play_game_msg)

        # create a new game if needed (choose character, background, etc)

        if sprint_id:
            sprint_select = {'text': sprint_id, 'msg': 'input'}
        else:
            sprint_select = {'text': 'j', 'msg': 'input'}
        # sprint_select = {'text': 'l', 'msg': 'input'} # large test sprint

        # species_select = {'text':'b','msg':'input'} # older version of crawl
        species_select = {'text': 'b', 'msg': 'input'}  # use this for most recent version of crawl
        background_select = {'text': 'h', 'msg': 'input'}
        weapon_select = {'text': 'a', 'msg': 'input'}
        game_creation_command_list = [sprint_select, species_select, background_select, weapon_select]
        for gm_create_cmd_msg in game_creation_command_list:
            time.sleep(2)  # give some delay
            logging.debug("Sending game creation selection command: " + str(gm_create_cmd_msg))
            await self.send_and_receive(gm_create_cmd_msg)

        time.sleep(1)

        # Make sure that autopickup is off (so we can learn drop and pickup actions)
        toggle_auto_pickup_msg = {'msg': 'key', 'keycode': 1}
        logging.debug("Sending toggle auto pickup so that it is off")
        await self.send_and_receive(toggle_auto_pickup_msg)

        time.sleep(1)

        # game loop
        logging.info("Beginning agent execution...")
        while not self.begin_shutdown:
            # ask for next action from agent
            next_agent_action = self.ai.next_action()

            # before we actually take the chosen action, update our context counts from previous state
            self.ai.update_context_counts()

            # execute action by sending it to the server
            if 'actions' in next_agent_action:
                actions = next_agent_action['actions']
                for a in actions:
                    next_agent_action = a.get_json()
                    print(next_agent_action)
                    msg_from_server = await self.send_and_receive(next_agent_action)
            else:
                print(next_agent_action)
                msg_from_server = await self.send_and_receive(next_agent_action)

            # let the agent know we've finished executing the action
            # self.ai.step_complete()

            print("Sent Action " + str(next_agent_action) + " And received:\n\t" + str(msg_from_server))

            if self.ai.ready_to_delete_game():
                pass
                # self.begin_shutdown = True
                # make sure to save data first
                # self.ai.save_data()
                # await self.end_session_and_quit_game()

            if not self.websocket.open:
                self.begin_shutdown = True
                # make sure to save data first
                self.ai.save_data()

        for task in asyncio.Task.all_tasks():
            task.cancel()

        time.sleep(5)

        # self.websocket.close()


def simple_connect_random_agent():
    pass


def main():
    game = GameConnection()
    game.connect()
    print("\n\nconnected!\n\n")
    agent = SimpleRandomAgent()
    # agent = FastDownwardPlanningAgent()

    setup_actions = agent.get_game_mode_setup_actions()
    for action in setup_actions:
        print("\n\nexecution action {}\n\n".format(action))
        game.send_and_receive_dict(action)

    # turn

    print("\n\nAbout to start playing the game \n\n")
    game_state = game.get_gamestate()
    i = 0
    while not game_state.has_agent_died():
        # print(game_state.draw_cell_map())

        next_action = agent.get_action(game_state)
        if next_action not in Action.command_to_msg.keys():
            print("Action {} is not implemented yet, skipping for now".format(next_action))
            continue

        game.send_and_receive_command(next_action)
        game_state = game.get_gamestate()
        i += 1

    if game_state.has_agent_died():
        # Quit and delete the game
        game.send_and_receive_command(Command.ABANDON_CURRENT_CHARACTER_AND_QUIT_GAME)
        game.send_and_receive_command(Command.RESPOND_YES_TO_PROMPT)
        game.send_and_receive_command(Command.ENTER_KEY)
        game.send_and_receive_command(Command.ENTER_KEY)
        game.send_and_receive_command(Command.ENTER_KEY)

    game.close()


if __name__ == "__main__":
    wc = WebTilesConnection()
    asyncio.get_event_loop().run_until_complete(wc.run())

#
# HUMAN_INPUT = False
# if len(sys.argv) >= 2:
#     if 'human' in sys.argv[1]:
#         HUMAN_INPUT = True
#
# if os.path.exists(crawl_socketpath) and not os.path.exists(socketpath):
#
#     primary = True
#
#     crawl_socket = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
#     crawl_socket.settimeout(10)
#
#     crawl_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#
#     if (crawl_socket.getsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF) < 2048):
#         crawl_socket.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 2048)
#
#     if (crawl_socket.getsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF) < 212992):
#         crawl_socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 212992)
#
#     msg = json_encode({
#             "msg": "attach",
#             "primary": primary
#             })
#
#     with warnings.catch_warnings():
#         warnings.simplefilter("ignore")
#
#     crawl_socket.bind(socketpath)
#
#     send_message(msg)
#
#     read_msgs()
#
#     # This will get all the state from the game at once
#     # Parsing error with json library
#     # msg = json_encode({
#     #         "msg": "spectator_joined"
#     #         })
#     #send_message(msg)
#
#
#
#     #do_sprint()
#     do_dungeon()
#
#     # turn off auto pick-up
#     control_input('A')
#     read_msgs()
#
#     # # Get Stone
#     # send_and_receive(dir_map['NW'])
#     # send_and_receive('g')
#
#     # move some random steps but don't walk into walls
#     i = 0
#     while( i < 5000 ):
#         action_str = "Action %3d - " % (i+1)
#
#         if HUMAN_INPUT:
#             human_pressed_key = input('Your Next Action')
#             if human_pressed_key == "":
#                 human_pressed_key = '\r'
#             send_and_receive(human_pressed_key)
#         else:
#             direction = random.choice(list(dir_map.keys()))
#             send_and_receive(dir_map[direction])
#             # if game_state.can_move_direction(direction):
#             #     action_str += " Moving %s..." % direction
#             #     send_and_receive(dir_map[direction])
#             # elif game_state.can_open_door(direction):
#             #     action_str += " Opening %s door..." % direction
#             #     send_and_receive(dir_map[direction])
#             # elif game_state.can_attack_monster(direction):
#             #     action_str += " Attacking monster %s..." % direction
#             #     send_and_receive(dir_map[direction])
#             # else:
#             #     continue
#
#             if game_state.agent_just_leveled_up():
#                 print("Woohooo we leveled up!!!!!!!!")
#                 send_input('\r')
#
#             if game_state.is_agent_too_terrified():
#                 print("FIX ME")
#                 time.sleep(10)
#
#             if game_state.agent_cannot_move():
#                 print("FIX ME")
#                 time.sleep(10)
#
#             if game_state.has_agent_died():
#                 print("******* AW MAN ... WE DIED ***********")
#                 time.sleep(1)
#                 send_input('\r')
#                 time.sleep(1)
#                 send_input('\r')
#                 time.sleep(1)
#                 send_input('\r')
#                 break
#
#             if game_state.game_has_more_messages(reset=True):
#                 print("more prompt!")
#                 send_and_receive('\r')
#
#         #time.sleep(1)
#         game_state.draw_cell_map()
#         print("------------printing raduis of 8 around agent------------")
#         game_state.cellmap.print_radius_around_agent(r=8)
#         print("Player's current position is {},{}".format(game_state.agent_x, game_state.agent_y))
#         #print("Tiles around agent are: {}".format(game_state.get_tiles_around_player_radius()))
#         game_state.print_inventory()
#
#         i = i + 1
#         print(action_str)
#
#     if not game_state.has_agent_died():
#         # Quit and delete the game
#         control_input('Q')
#         time.sleep(1)
#         send_input('yes\r')
#         time.sleep(1)
#         send_input('\r')
#         time.sleep(1)
#         send_input('\r')
#         time.sleep(1)
#         send_input('\r')
#
#     close()
#
#     #print("Map Boundaries : %s" % str(game_state.map_obj.get_bounds()))
# else:
#     print('%s does not exist' % crawl_socketpath)
