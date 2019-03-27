'''
This class contains a variety of utilities that support playing the game by sending and receiving communication
to the server
'''

import asyncio
import websockets
import zlib
import json
import time
import logging
import sys

# custom
import actions
import agent
import simple_planning_agent
import relational_learning_agent

with open('config.json', 'r') as f:
    config = json.load(f)

logging.basicConfig(level=logging.DEBUG)

decomp = zlib.decompressobj(-zlib.MAX_WBITS)

# WebTiles refers to Dungeon Crawl Stone Soup (tiles version) played
# via a webserver
class WebTilesConnection():

    last_msg_from_server = {}

    def __init__(self, ai:agent.CrawlAIAgent):
        self.websocket = None
        self.logged_in = False
        self.ai = ai

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
                        
        except:
            print("Ignoring unparseable JSON (error: %s): %s.", e.args[0], json_message)

    async def send_key_action(self, key_action_id):

        # send the message
        await self.websocket.send(json.dumps(actions.key_actions[key_action_id]))
    
        # wait for server to get back
        data_recv = await self.websocket.recv()
        data_recv += bytes([0,0,255,255])
        json_message = decomp.decompress(data_recv)
        json_message = json_message.decode("utf-8")    

        msg_from_server = json.loads(json_message)
        return msg_from_server
    
    async def send_text_action(self, text_key):
    
        # send the message
        await self.websocket.send(json.dumps(actions.text_actions[text_key]))
        
        # wait for server to get back
        data_recv = await self.websocket.recv()
        data_recv += bytes([0,0,255,255])
        json_message = decomp.decompress(data_recv)
        json_message = json_message.decode("utf-8")

        msg_from_server = json.loads(json_message)
        return msg_from_server        

    async def send(self, message):
        '''
        message needs to be a dict and contain msg key
        '''
        if 'msg' not in message:
            raise Exception("Message dict must contain a 'msg' key")

        await self.websocket.send(json.dumps(message)) 

    async def run(self):

        logging.debug("About to connect to uri: " + str(config['server_uri']))
        self.websocket = await websockets.connect(config['server_uri'])
        logging.info("Connected to web server:" + str(self.websocket and self.websocket.open))
        logging.debug("About to send login msg")
        await self.websocket.send(json.dumps(config['login_msg']))
        logging.debug("just sent login msg")

        data_recv = await self.websocket.recv()
        data_recv += bytes([0, 0, 255, 255])
        json_message = decomp.decompress(data_recv)
        json_message = json_message.decode("utf-8")
        # message = json.loads(json_message)
        try:
            msg_from_server = json.loads(json_message)
            logging.debug("msg_from_server is " + str(msg_from_server))
        except ValueError as e:
            logging.warning("Ignoring unparseable JSON (error: %s): %s.", e.args[0], json_message)

        msgs = []
        if 'msgs' in msg_from_server.keys():
            msgs = msg_from_server['msgs']

        for msg_i in msgs:
            if msg_i['msg'] == 'ping':
                logging.debug("Received message ping from server, about to send pong")
                await self.send({'msg': 'pong'})

        data_recv = await self.websocket.recv()
        data_recv += bytes([0, 0, 255, 255])
        json_message = decomp.decompress(data_recv)
        json_message = json_message.decode("utf-8")
        try:
            msg_from_server = json.loads(json_message)
            logging.debug("msg_from_server is " + str(msg_from_server))
        except ValueError as e:
            logging.warning("Ignoring unparseable JSON (error: %s): %s.", e.args[0], json_message)

        # start the trunk game
        # game_id = 'dcss-web-trunk'
        game_id = 'sprint-web-trunk'
        play_game_msg = {'msg': 'play', 'game_id': game_id}

        await self.websocket.send(json.dumps(play_game_msg))
        logging.debug("just sent play game msg")

        data_recv = await self.websocket.recv()
        data_recv += bytes([0, 0, 255, 255])
        json_message = decomp.decompress(data_recv)
        json_message = json_message.decode("utf-8")
        try:
            msg_from_server = json.loads(json_message)
            self.pretty_print_server_msg(msg_from_server)

        except ValueError as e:
            logging.warning("Ignoring unparseable JSON (error: %s): %s.", e.args[0], json_message)


        if self.create_new_game:
            # species = minotaur , keycode 'n'
            # sprint_select = {'text': 'j', 'msg': 'input'}
            # species_select = {'text': 'n', 'msg': 'input'}
            # background_select = {'text': 'h', 'msg': 'input'}
            # weapon_select = {'text': 'd', 'msg': 'input'}
            # time.sleep(3)
            # game_creation_command_list = [sprint_select, species_select, background_select, weapon_select]
            game_creation_command_list = [self.ai.game_mode_selection(),
                                          self.ai.species_selection(),
                                          self.ai.background_selection(),
                                          self.ai.weapon_selection()]
            for gm_create_cmd_msg in game_creation_command_list:
                await self.websocket.send(json.dumps(gm_create_cmd_msg))
                logging.debug("just sent game creation selection command: " + str(gm_create_cmd_msg))

                data_recv = await self.websocket.recv()
                data_recv += bytes([0, 0, 255, 255])
                json_message = decomp.decompress(data_recv)
                json_message = json_message.decode("utf-8")
                try:
                    msg_from_server = json.loads(json_message)
                    self.last_msg_from_server = msg_from_server
                    self.pretty_print_server_msg(msg_from_server)

                except ValueError as e:
                    logging.warning("Ignoring unparseable JSON (error: %s): %s.", e.args[0], json_message)
                time.sleep(2)

        # END GAME SETUP

        async def move(direction=''):
            if direction is 'left':
                await self.websocket.send(json.dumps(move_left_msg))
            elif direction is 'right':
                await self.websocket.send(json.dumps(move_right_msg))
            elif direction is 'up':
                await self.websocket.send(json.dumps(move_up_msg))
            elif direction is 'down':
                await self.websocket.send(json.dumps(move_down_msg))
            else:
                logging.error('Tried to move in direction %s', direction)

            # wait for server to get back
            data_recv = await self.websocket.recv()
            data_recv += bytes([0, 0, 255, 255])
            json_message = decomp.decompress(data_recv)
            json_message = json_message.decode("utf-8")
            try:
                msg_from_server = json.loads(json_message)
                self.pretty_print_server_msg(msg_from_server)

            except ValueError as e:
                print("Ignoring unparseable JSON (error: %s): %s.", e.args[0], json_message)

            time.sleep(delay)

        ### LOAD THE AI HERE ###

        time.sleep(0.5)
        print("Agent is about to start playing ...")
        time.sleep(0.5)

        delay = 1

        if len(sys.argv) > 1:
            agent1 = simple_planning_agent.SimplePlanningAgent(sys.argv[1])
        else:
            agent1 = simple_planning_agent.SimplePlanningAgent('~/Documents/Repos/Metric-FF-v2.1/ff')

        agent1.update(self.last_msg_from_server)

        while True:

            next_agent_action = agent1.get_next_action()
            if next_agent_action in actions.key_actions.keys():
                msg = await self.send_key_action(next_agent_action, )
            elif next_agent_action in actions.text_actions.keys():
                msg = await self.send_text_action(next_agent_action)

            self.pretty_print_server_msg(msg)

            # check for game ending and skip through result screens...
            for msgblob in msg["msgs"]:
                if "messages" in msgblob:
                    for message in msgblob["messages"]:
                        if "text" in message:
                            if message["text"].find('You have escaped!') != -1:
                                print("The Agent %s has escaped the dungeon" % login_msg['username'])
                                return
                            elif message["text"].find('You die...') != -1:
                                print("The Agent %s has died in the dungeon" % login_msg['username'])
                                return

            agent1.update(msg)
            time.sleep(delay)


if __name__ == "__main__":    

    agent = relational_learning_agent.RelationalLearningAgent()

    conn = WebTilesConnection(agent=agent)

    event_loop = asyncio.get_event_loop()
    try:
        event_loop.run_until_complete(conn.run())
    finally:
        event_loop.close()


