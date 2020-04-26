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

# custom
import actions
import gamestate

import simple_planning_agent
import relational_learning_agent
from exploratory_planning_agent import ExploratoryPlanningAgent

logging.basicConfig(level=logging.INFO)

server_uri = 'ws://localhost:8080/socket'

### CHANGE USERNAME AND PASSWORD HERE ###
login_msg = {'msg':'login',
             'username':'midca',
             'password':'meta'}

decomp = zlib.decompressobj(-zlib.MAX_WBITS)


# Messages for permanently quitting a session
initiate_quit_msg_1 = {'msg':'key', 'keycode':17} # Equivalent to Ctrl-q
confirm_quit_msg_2 = {'msg':'key', 'keycode':21}
confirm_quit_msg_3 = {'msg':'key', 'keycode':11}
confirm_quit_with_yes_4 = {'msg':'input', 'text':'yes\r'}
confirm_quit_clear_menu_via_enter_5 = {'msg':'input', 'text':'\r'}
confirm_quit_clear_menu_via_enter_6 = {'msg':'input', 'text':'\r'}

quit_messages_sequence = [initiate_quit_msg_1,
                          confirm_quit_msg_2,
                          confirm_quit_msg_3,
                          confirm_quit_with_yes_4,
                          confirm_quit_clear_menu_via_enter_5,
                          confirm_quit_clear_menu_via_enter_6]

# WebTiles refers to Dungeon Crawl Stone Soup (tiles version) played
# via a webserver
class WebTilesConnection():

    last_msg_from_server = {}

    def __init__(self, ai=None):
        self.websocket = None
        self.logged_in = False
        self.ai = ai
        self.recv_counter = 0
        self.CREATE_NEW_GAME = False

    def pretty_print_server_msg(self, msg_from_server):
        try:
            for msg in msg_from_server['msgs']:
                print("--> New Message from Server <--")
                #ignore_list = ['cell','html','content','skip']
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
                            print(str(key)+":"+str(msg[key]))
                        
        except Exception as e:
            print("Ignoring unparseable JSON (error: %s): %s.", e.args[0], msg_from_server)

    async def get_all_server_messages(self):
        i = 0
        SERVER_READY_FOR_INPUT = False
        while not SERVER_READY_FOR_INPUT:
            try:
                future = self.websocket.recv()
                #print("** AWAITING ON WEBSOCKET RECV in loop, i=" + str(i))
                data_recv = await asyncio.wait_for(future, timeout=0.5)
                #print("** POST-AWAITING ON WEBSOCKET RECV in loop, i=" + str(i))

                data_recv += bytes([0, 0, 255, 255])
                json_message = decomp.decompress(data_recv)
                json_message = json_message.decode("utf-8")
                msg_from_server = json.loads(json_message)
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
                logging.warning("i="+str(i)+"Ignoring unparseable JSON (error: %s): %s.", e.args[0], json_message)
            except asyncio.TimeoutError:
                # server is now ready for input
                SERVER_READY_FOR_INPUT = True
            i+=1

    async def send_and_receive(self, message):
        # send data to server
        #print("AWAITING ON WEBSOCKET_1 SEND - sending message: "+str(message))
        await self.websocket.send(json.dumps(message))
        #print("POST-AWAITING ON WEBSOCKET_1 SEND")
        # wait for server to get back

        await self.get_all_server_messages()

    async def end_session_and_quit_game(self):
        '''
        Sends the ctrl-q signal to the webserver to permamently end the game.
        :return:
        '''
        for quit_msg in quit_messages_sequence:
            await self.send_and_receive(quit_msg)

        
    async def run(self):
        # connect
        logging.debug("Connecting to URI "+str(server_uri)+ " ...")
        #print("AWAITING ON WEBSOCKET_3 CONNECT")
        self.websocket = await websockets.connect(server_uri)
        #print("POST-AWAITING ON WEBSOCKET_3 CONNECT")
        logging.info("Connected to webserver:"+str(self.websocket and self.websocket.open))

        # login
        logging.debug("Sending login message...")

        await self.send_and_receive(login_msg)

        # break apart msg from server
        #msgs = []
        #if 'msgs' in msg_from_server.keys():
        #    msgs = msg_from_server['msgs']

        # send pong
        #for msg_i in msgs:
        #    if msg_i['msg'] == 'ping':
        #        logging.debug("Received message ping from server, about to send pong")
        await self.websocket.send(json.dumps({'msg' : 'pong'}))

        time.sleep(0.5)

        # choose the game mode
        game_id = 'sprint-web-trunk'
        play_game_msg = {'msg':'play', 'game_id':game_id}
        await self.send_and_receive(play_game_msg)

        time.sleep(0.5)

        # create a new game if needed (choose character, background, etc)
        sprint_select = {'text':'l','msg':'input'} # this chooses the sprint level
        #species_select = {'text':'b','msg':'input'} # older version of crawl
        species_select = {'text': 'b', 'msg': 'input'}  # use this for most recent version of crawl
        background_select = {'text':'h','msg':'input'}
        weapon_select = {'text':'a','msg':'input'}
        game_creation_command_list = [sprint_select,species_select,background_select,weapon_select]
        for gm_create_cmd_msg in game_creation_command_list:
            time.sleep(1)  # give some delay
            logging.debug("Sending game creation selection command: " + str(gm_create_cmd_msg))
            await self.send_and_receive(gm_create_cmd_msg)

        time.sleep(1)



        # game loop
        while True:
            next_agent_action = self.ai.next_action()
            msg_from_server = await self.send_and_receive(next_agent_action)
            print("Sent Action "+str(next_agent_action)+ " And received:\n\t"+str(msg_from_server))

            if self.ai.ready_to_delete_game():
                self.ai.save_data()
                await self.end_session_and_quit_game()
                break

        await self.end_session_and_quit_game()


def single_run(action_selection_type_str=None):
    ai = relational_learning_agent.RelationalLearningAgent()

    agent_file_name = str(ai) + '-' + datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d--%H-%M-%S')
    ai.set_data_filename(agent_file_name)

    ai.set_action_selection(type_str=action_selection_type_str)

    conn = WebTilesConnection(ai=ai)

    def _graceful_exit(signal, frame):
        try:
            ai.save_data()
            conn.end_session_and_quit_game()
            sys.exit()
        except Exception as e:
            print("Encountered error {} - data may not have been saved, exiting now".format(e))
            sys.exit()

    # gracefully save data when exiting via ctrl-c
    signal.signal(signal.SIGINT, _graceful_exit)

    event_loop = asyncio.get_event_loop()
    try:
        event_loop.run_until_complete(conn.run())
    finally:
        event_loop.close()


if __name__ == "__main__":
    agent_action_selection_types = ['explore','random','human']

    for action_type_str in agent_action_selection_types:
        single_run(action_type_str)

        print("Sleeping for 10 seconds before next round starts....")
        time.sleep(10)
