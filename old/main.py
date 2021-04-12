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

# custom
import actions
import states

#import simple_planning_agent
#import relational_learning_agent

logging.basicConfig(level=logging.INFO)

server_uri = 'ws://localhost:8080/socket'

### CHANGE USERNAME AND PASSWORD HERE ###
login_msg = {'msg':'login',
             'username':'midca',
             'password':'midca'}

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

#json_messages_from_server_file = open('json_server_messages.json','w')

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
        self.game_ended = False
        self.begin_shutdown = False

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
        request_pong = False
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

                if 'msgs' in msg_from_server:
                    for msg in msg_from_server['msgs']:
                        if 'msg' in msg:
                            if msg['msg']  == "ping":
                                request_pong = True

                #json_messages_from_server_file.write(pprint.pformat(msg_from_server,indent=2)+'\n')
                #json_messages_from_server_file.flush()

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
            except asyncio.CancelledError:
                logging.info('Received message to cancel - ignoring so recv can finish up')
                self.begin_shutdown = True
            except asyncio.TimeoutError:
                # server is now ready for input
                SERVER_READY_FOR_INPUT = True
            #except Exception as e:
            #    logging.warning("Caught exception {} in get_all_server_messages()".format(e))
            i+=1

        if request_pong:
            await self.websocket.send(json.dumps({"msg" : "pong"}))

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
        if not self.game_ended:
            for quit_msg in quit_messages_sequence:
                await self.send_and_receive(quit_msg)

            self.game_ended = True

        logging.info("Sent all quit messages, game is deleted...")
        
    async def run(self, sprint_id=None):
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

        # create a new game if needed (choose character, background, etc)

        if sprint_id:
            sprint_select = {'text': sprint_id, 'msg': 'input'}
        else:
            sprint_select = {'text':'j','msg':'input'}
        # sprint_select = {'text': 'l', 'msg': 'input'} # large test sprint

        #species_select = {'text':'b','msg':'input'} # older version of crawl
        species_select = {'text': 'b', 'msg': 'input'}  # use this for most recent version of crawl
        background_select = {'text':'h','msg':'input'}
        weapon_select = {'text':'a','msg':'input'}
        game_creation_command_list = [sprint_select,species_select,background_select,weapon_select]
        for gm_create_cmd_msg in game_creation_command_list:
            time.sleep(2)  # give some delay
            logging.debug("Sending game creation selection command: " + str(gm_create_cmd_msg))
            await self.send_and_receive(gm_create_cmd_msg)

        time.sleep(1)

        # Make sure that autopickup is off (so we can learn drop and pickup actions)
        toggle_auto_pickup_msg = {'msg':'key', 'keycode':1}
        logging.debug("Sending toggle auto pickup so that it is off")
        await self.send_and_receive(toggle_auto_pickup_msg)

        time.sleep(1)

        # game loop
        logging.info("Beginning agent execution...")
        while not self.begin_shutdown:
            # ask for next action from agent
            next_agent_action = self.ai.next_action()

            # before we actually take the chosen action, update our context counts from previous states
            self.ai.update_context_counts()

            # execute action by sending it to the server
            if 'actions' in next_agent_action:
                actions = next_agent_action['actions']
                for a in actions:
                    next_agent_action=a.get_json()
                    print(next_agent_action)
                    msg_from_server = await self.send_and_receive(next_agent_action)
            else:
                print(next_agent_action)
                msg_from_server = await self.send_and_receive(next_agent_action)

            # let the agent know we've finished executing the action
            #self.ai.step_complete()

            print("Sent Action "+str(next_agent_action)+ " And received:\n\t"+str(msg_from_server))

            if self.ai.ready_to_delete_game():
                pass
                #self.begin_shutdown = True
                # make sure to save data first
                #self.ai.save_data()
                #await self.end_session_and_quit_game()

            if not self.websocket.open:
                self.begin_shutdown = True
                # make sure to save data first
                self.ai.save_data()

        for task in asyncio.Task.all_tasks():
            task.cancel()

        time.sleep(5)

        #self.websocket.close()

def single_run(action_selection_type_str=None,context_size=3,sprint_id='j'):
    ai = relational_learning_agent.RelationalLearningAgent(action_type_str=action_selection_type_str,context_size=context_size,sprint_id=sprint_id)
    #ai = simple_planning_agent.SimplePlanningAgent('/Users/Decker/Documents/Repos/Metric-FF-v2.1/ff')

    if action_selection_type_str:
        agent_file_name = '{0}-{1}-action_{2}-context_size_{3}-sprint_id_{4}.csv'.format(str(ai),datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d--%H-%M-%S'),action_selection_type_str,context_size,sprint_id)
    else:
        agent_file_name = str(ai) + '-' + datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d--%H-%M-%S')+'.csv'

    ai.set_data_filename(agent_file_name)

    conn = WebTilesConnection(ai=ai)

    def _graceful_exit(signal, frame):
            #ai.save_data()
        try:
            print("Caught Interrupt...Wrapping up, please wait a little bit...")
            ai.ready_to_delete_game()
            time.sleep(2)
        except Exception as e:
            print("Encountered error {} - data may not have been saved, exiting now".format(e))
            #sys.exit()
        sys.exit()

    # gracefully save data when exiting via ctrl-c
    signal.signal(signal.SIGINT, _graceful_exit)

    event_loop = asyncio.get_event_loop()
    try:
        event_loop.run_until_complete(conn.run(sprint_id=sprint_id))
    finally:
        for task in asyncio.Task.all_tasks():
            task.cancel()

        event_loop.close()

        #json_messages_from_server_file.close()

if __name__ == "__main__":

    cli_args = sys.argv
    if len(cli_args) > 1:
        c = int(cli_args[2])
        m = cli_args[3]
        a = cli_args[1]

        single_run(a,context_size=c,sprint_id=m)

    else:
        print("Required argument: type of action selection, one of [random,explore,human]")



