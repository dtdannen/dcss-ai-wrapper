import asyncio
import errno
import fcntl
import os
import os.path
import pty
import resource
import signal
import struct
import sys
import termios
import time
import logging
import json

from tornado.escape import json_decode, json_encode, utf8
from tornado.ioloop import IOLoop

from dcss.connection.config import LocalConfig
from game_connection_base import GameConnectionBase


class GameConnectionLocal(GameConnectionBase):

    def __init__(self):
        super().__init__()
        logging.debug("Initializing GameConnectionLocal()")
        self.socket_path = "/home/dustin/Projects/crawl/crawl-ref/source/rcs/midca:test.sock"
        self.call = ["./home/dustin/Projects/crawl/crawl-ref/source/crawl",
                     "-name",   LocalConfig.agent_name,
                     "-rc", LocalConfig.rc,
                     "-macro",  LocalConfig.macro,
                     "-morgue", LocalConfig.morgue,
                     "-webtiles-socket", self.socket_path,
                     "-await-connection"]

        #self.output_callback = self._on_process_output
        self.agentResponseLoopGenerator = None
        self.asyncio_loop = None
        self.output_buffer = b""
        self.we_are_parent = None
        self.we_are_child = None
        self.child_already_created = None

        self._start_process()

        logging.debug("[parent] about to run asyncio.get_event_loop()")
        self.asyncio_loop = asyncio.get_event_loop()

        try:
            logging.debug("[parent] about to run asyncio_loop.run_forever()")
            self.asyncio_loop.run_forever()
        finally:
            self.asyncio_loop.stop()
            self.asyncio_loop.close()

    def get_logger(pid):
        file_name = 'logs/child_primes_{}.log'.format(pid)
        file_handler = logging.FileHandler(file_name)
        name = 'child:{}'.format(pid)
        logger = logging.getLogger(name)
        logger.addHandler(file_handler)
        # TODO: Add a formater here
        return logger

    def _launch_crawl_process(self, errpipe_write):
        def handle_signal(signal, f):
            sys.exit(0)

        signal.signal(1, handle_signal)

        # Set window size
        cols, lines = (80, 24)
        s = struct.pack("HHHH", lines, cols, 0, 0)
        fcntl.ioctl(sys.stdout.fileno(), termios.TIOCSWINSZ, s)

        os.close(self.errpipe_read)
        os.dup2(errpipe_write, 2)

        # Make sure not to retain any files from the parent
        max_fd = resource.getrlimit(resource.RLIMIT_NOFILE)[0]
        for i in range(3, max_fd):
            try:
                os.close(i)
            except OSError:
                pass

        # And exec
        env = dict(os.environ)
        #env.update(self.env_vars)  #TODO do we need this? - it had game id in it
        env["COLUMNS"] = str(cols)
        env["LINES"] = str(lines)
        env["TERM"] = "linux"
        #if self.game_cwd:
        #    os.chdir(self.game_cwd)
        try:
            # this launches crawl
            logging.debug("[child] Launching crawl with call: {}".format(self.call))
            os.execvpe(self.call[0], self.call, env)
            logging.debug("[child] Post crawl launch")
        except OSError:
            sys.exit(1)

    def _start_process(self):
        if self.child_already_created:
            return

        try:  # Unlink if necessary
            os.unlink(self.socket_path)
        except OSError as e:
            if e.errno != errno.ENOENT:
                raise

        self.errpipe_read, errpipe_write = os.pipe()

        logging.debug("[parent] About to fork into child and parent")
        self.pid, self.child_fd = pty.fork()
        self.child_already_created = True

        if self.pid == 0:
            # We're the child
            self.we_are_parent = False
            self.we_are_child = True
            logging.debug("[child] About to launch crawl on the child process")
            self._launch_crawl_process(errpipe_write)
        else:
            # We're the parent
            self.we_are_parent = True
            self.we_are_child = False
            os.close(errpipe_write)

            logging.debug("[parent] About to continue on parent process")

            self.asyncio_loop = asyncio.get_event_loop()

            logging.debug("[parent] Adding reader handle_read to asyncio loop")

            # TODO: Have to first get the loop object.
            self.asyncio_loop.add_reader(self.child_fd,
                                         self._handle_read)

            # TODO come back and make sure we handle err read
            #self.asyncio_loop.add_reader(self.child_fd,
            #                             self._handle_err_read)

            time.sleep(1)
            print("About to send game play message")
            play_game_msg = {'msg': 'play', 'game_id': 'dcss-web-trunk'}
            #                 self.sendMessage(json.dumps(play_game_msg).encode('utf-8'))
            self.write_input(json.dumps(play_game_msg).encode('utf-8'))
            print("Sent send game play message")

            # Old code using Tornado:
            '''
            IOLoop.current().add_handler(self.child_fd,
                                         self._handle_read,
                                         IOLoop.ERROR | IOLoop.READ)
    
            IOLoop.current().add_handler(self.errpipe_read,
                                         self._handle_err_read,
                                         IOLoop.READ)
            '''

    #  Functions that handle directing the output of the crawl binary to the
    #  agent program.
    def _handle_read(self):
        if self.we_are_parent and self.child_fd:
            BUFSIZ = 2048
            try:
                logging.debug("[parent] before buf = os.read()")
                buf = os.read(self.child_fd, BUFSIZ)  # todo find what BUFSIZ used to be
                logging.debug("[parent] buf after os.read() = {}".format(buf))
                if len(buf) > 0:
                    #self.write_ttyrec_chunk(buf)
                    self.output_buffer += buf
                    self._do_output_callback()
            except:
                pass

            # JTS
            # What is being read here is from the file descriptor of the
            # terminal program crawl. That is output from the crawl program.
            '''
            if events & self.io_loop.READ:
                buf = os.read(fd, BUFSIZ)

                if len(buf) > 0:
                    self.write_ttyrec_chunk(buf)

                    if self.activity_callback:
                        self.activity_callback()

                    self.output_buffer += buf
                    self._do_output_callback()

                self.poll()

            if events & self.io_loop.ERROR:
                self.poll()
            '''

    def _do_output_callback(self):
        # JTS
        # Gets position of the end of the first line in the buffer
        pos = self.output_buffer.find("\n")
        while pos >= 0:
            line = self.output_buffer[:pos]
            self.output_buffer = self.output_buffer[pos + 1:]

            if len(line) > 0:
                if line[-1] == "\r": line = line[:-1]

                self._on_process_output(line)
                '''
                #if self.output_callback:
                if True:
                    # JTS
                    # This would be the _on_process_output() method in the
                    # CrawlProcessHandler object, which ultimately calls the
                    # write_message() method of the CrawlWebSocket object.
                    # This goes back to the player's browser.
                    #self.output_callback(line)
                    self._on_process_output(line)
                '''
            pos = self.output_buffer.find("\n")


    def _on_process_output(self, line):
        # This was copied over from the class CrawlProcessHandler and ends up getting assigned to
        # the output_callback method of this class (which is a rewrite of TerminalRecorder in the
        # Crawl repository.

        #self.check_where()

        try:
            # TODO: swap out for non Tornado version:
            json_decode(line)
        except ValueError:
            logging.warning("Invalid JSON output from Crawl process: %s", line)

        self.write_message(line, True)

        # send messages from wrapper scripts only to the player
        # for receiver in self._receivers:
        #     if not receiver.watched_game:
        #         receiver.write_message(line, True)

    def write_message(self, msg, send=True):
        #if self.client_closed: return
        self.message_queue.append(utf8(msg))
        if send:
            self.flush_messages()

    def flush_messages(self):
        #if self.client_closed or len(self.message_queue) == 0:
        if len(self.message_queue) == 0:
            return
        msg = "{\"msgs\":[" + ",".join(self.message_queue) + "]}"
        self.message_queue = []

        try:
            #self.total_message_bytes += len(msg)
            #self.uncompressed_bytes_sent += len(msg)
            self.send_message_to_agent(msg)

            #super(CrawlWebSocket, self).write_message(msg)
        except Exception as e:
            logging.warning("Exception trying to send message.", exc_info = True)
            raise e

    def get_next_message(self):
        if len(self.message_queue) > 0:
            return self.message_queue.pop()
        else:
            return None



    def send_message_to_agent(self, message, binary=False):
        # Do something here
        self.receive_message_from_crawl(message, binary)
    # End of functions that handle directing the output of the crawl binary to the
    # agent program.
    #

    def receive_message_from_crawl(self, payload, isBinary):
        print("Message {} recieved: isBinary={}".format(self.messages_received_counter, isBinary))
        self.messages_received_counter += 1
        message_as_str = None
        if isBinary:
            print("Binary message received: {0} bytes".format(len(payload)))
            payload += bytes([0, 0, 255, 255])
            json_message = self.decomp.decompress(payload)
            json_message_decoded = json_message.decode("utf-8")
            print("   Decoding turns it into: {}".format(json_message_decoded))
            message_as_str = json_message_decoded
        else:
            print("Text message received: {0}".format(payload.decode('utf-8')))
            message_as_str = payload.decode('utf-8')
        '''
        print("****************************************************************************")
        print("Message Number: " + str(self.messages_received_counter))
        print(message_as_str)
        print("****************************************************************************")
        '''

        message_as_json = {}
        try:
            message_as_json = json.loads(message_as_str)
        except:
            print(
                "Failure to parse message_as_json\n****** you may have spectated too soon, best thing to do is just to restart the agent ******")
            time.sleep(20)

        self.game_state.update(message_as_json)

        self.perform_state_checks(message_as_json)

        # this must come AFTER perform_state_checks()
        self.game_state.set_current_menu(self._IN_MENU)

        if self.agentResponseLoopGenerator != None:
            next(self.agentResponseLoopGenerator)


    async def setupAgentResponseLoop(self):
        print("WebSocket connection open.")
        # start sending messages every second ..

        self.agentResponseLoopGenerator = self.agentResponseLoop()

    # def agentResponseLoop(self):
    #     times = []
    #     save_time_delay = 4.
    #     last_saved_time = None
    #
    #
    #
    #
    #
    #     while True:
    #         if self._CONNECTED and self._NEEDS_PONG:
    #             print("SENDING PONG MESSAGE")
    #             pong_msg = {"msg": "pong"}
    #             self.sendMessage(json.dumps(pong_msg).encode('utf-8'))
    #             self._NEEDS_PONG = False
    #         elif self._CONNECTED and self._NEEDS_ENTER:
    #             print("SENDING ENTER KEY BECAUSE OF PROMPT")
    #             enter_key_msg = {"text": "\r", "msg": "input"}
    #             self.sendMessage(json.dumps(enter_key_msg).encode('utf-8'))
    #             self._NEEDS_ENTER = False
    #         else:
    #             if self._CONNECTED and not self._LOGGED_IN:
    #                 print("SENDING LOGIN MESSAGE")
    #                 login_msg = {'msg': 'login',
    #                              'username': self.config.agent_name,
    #                              'password': self.config.agent_password}
    #                 self.sendMessage(json.dumps(login_msg).encode('utf-8'))
    #
    #             elif self._LOGGED_IN and self._IN_LOBBY and not self._GAME_STARTED:
    #                 print("SENDING GAME MODE SELECTION MESSAGE")
    #                 play_game_msg = {'msg': 'play', 'game_id': self.config.game_id}
    #                 self.sendMessage(json.dumps(play_game_msg).encode('utf-8'))
    #
    #             #### BEGIN SEEDED GAME MENU NAVIGATION ####
    #             elif self.config.game_id == 'seeded-web-trunk' and self._IN_GAME_SEED_MENU and not self._SENT_GAME_SEED:
    #                 print("SENDING GAME SEED")
    #                 game_seed_msg = {"text": str(config.WebserverConfig.seed), "generation_id": 1, "widget_id": "seed",
    #                                  "msg": "ui_state_sync"}
    #                 self.sendMessage(json.dumps(game_seed_msg).encode('utf-8'))
    #                 self._SENT_GAME_SEED = True
    #
    #             elif self.config.game_id == 'seeded-web-trunk' and self._SENT_GAME_SEED and not self._CHECKED_BOX_FOR_PREGENERATION:
    #                 print("SENDING CHECKMARK TO CONFIRM PREGENERATION OF DUNGEON")
    #                 pregeneration_checkbox_msg = {"checked": True, "generation_id": 1, "widget_id": "pregenerate",
    #                                               "msg": "ui_state_sync"}
    #                 self.sendMessage(json.dumps(pregeneration_checkbox_msg).encode('utf-8'))
    #                 self._CHECKED_BOX_FOR_PREGENERATION = True
    #
    #             elif self.config.game_id == 'seeded-web-trunk' and self._READY_TO_SEND_SEED_GAME_START and self._SENT_GAME_SEED and self._CHECKED_BOX_FOR_PREGENERATION and not self._SENT_SEEDED_GAME_START:
    #                 print("SENDING MESSAGE TO START THE SEEDED GAME WITH CLICK BUTTON MESSAGE")
    #                 start_seeded_game_msg_button = {"generation_id": 1, "widget_id": "btn-begin",
    #                                                 "msg": "ui_state_sync"}
    #                 self.sendMessage(json.dumps(start_seeded_game_msg_button).encode('utf-8'))
    #                 self._SENT_SEEDED_GAME_START = True
    #
    #             elif self.config.game_id == 'seeded-web-trunk' and self._SENT_SEEDED_GAME_START and not self._SENT_SEEDED_GAME_START_CONFIRMATION:
    #                 print("SENDING MESSAGE TO CONFIRM THE SEEDED GAME WITH CLICK BUTTON MESSAGE")
    #                 confirm_seeded_game_msg_button = {"keycode": 13, "msg": "key"}
    #                 self.sendMessage(json.dumps(confirm_seeded_game_msg_button).encode('utf-8'))
    #                 self._SENT_SEEDED_GAME_START_CONFIRMATION = True
    #             #### END SEEDED GAME MENU NAVIGATION ####
    #
    #             #### BEGIN TUTORIAL GAME MENU NAVIGATION ####
    #             elif self.config.game_id == 'tut-web-trunk' and self._IN_MENU == Menu.TUTORIAL_SELECTION_MENU:
    #                 print("SENDING MESSAGE TO SELECT THE TUTORIAL #{} IN THE TUTORIAL MENU".format(
    #                     config.WebserverConfig.tutorial_number))
    #                 hotkey = MenuBackgroundKnowledge.tutorial_lesson_number_to_hotkey[
    #                     config.WebserverConfig.tutorial_number]
    #                 tutorial_lesson_selection_message = {"keycode": hotkey, "msg": "key"}
    #                 self.sendMessage(json.dumps(tutorial_lesson_selection_message).encode('utf-8'))
    #                 self._IN_MENU = Menu.NO_MENU
    #                 self._CREATED_A_NEW_CHARACTER = True
    #             #### END TUTORIAL GAME MENU NAVIGATION ####
    #
    #             #### BEGIN TUTORIAL GAME MENU NAVIGATION ####
    #             elif self.config.game_id == 'sprint-web-trunk' and self._IN_MENU == Menu.SPRINT_MAP_SELECTION_MENU:
    #                 print("SENDING MESSAGE TO SELECT THE TUTORIAL #{} IN THE SPRINT MENU".format(
    #                     config.WebserverConfig.tutorial_number))
    #                 hotkey = MenuBackgroundKnowledge.sprint_map_letter_to_hotkey[
    #                     config.WebserverConfig.sprint_map_letter]
    #                 sprint_map_selection_message = {"keycode": hotkey, "msg": "key"}
    #                 self.sendMessage(json.dumps(sprint_map_selection_message).encode('utf-8'))
    #                 self._IN_MENU = Menu.NO_MENU
    #             #### END TUTORIAL GAME MENU NAVIGATION ####
    #
    #             elif self._GAME_STARTED:
    #                 if self._IN_MENU == Menu.CHARACTER_CREATION_SELECT_SPECIES and not self._SENT_SPECIES_SELECTION:
    #                     if self.config.species not in self.species_options.keys():
    #                         print(
    #                             "ERROR species {} specified in config is not available. Available choices are: {}".format(
    #                                 self.config.species, self.species_options.keys()))
    #                     else:
    #                         species_selection_hotkey = self.species_options[self.config.species]
    #                         species_selection_msg = self.get_hotkey_json_as_msg(species_selection_hotkey)
    #                         print("SENDING SPECIES SELECTION MESSAGE OF: {}".format(species_selection_msg))
    #                         self._SENT_SPECIES_SELECTION = True
    #                         # Right before we send the message, clear the menu - this only fails if the message being sent fails
    #                         self._IN_MENU = Menu.NO_MENU
    #                         self.sendMessage(json.dumps(species_selection_msg).encode('utf-8'))
    #
    #                 if self._IN_MENU == Menu.CHARACTER_CREATION_SELECT_BACKGROUND and not self._SENT_BACKGROUND_SELECTION:
    #                     if self.config.background not in self.background_options.keys():
    #                         print(
    #                             "ERROR background {} specified in config is not available. Available choices are: {}".format(
    #                                 self.config.background, self.background_options.keys()))
    #                     else:
    #                         background_selection_hotkey = self.background_options[self.config.background]
    #                         background_selection_msg = self.get_hotkey_json_as_msg(background_selection_hotkey)
    #                         print("SENDING BACKGROUND SELECTION MESSAGE OF: {}".format(background_selection_msg))
    #                         self._SENT_BACKGROUND_SELECTION = True
    #                         self._CREATED_A_NEW_CHARACTER = True
    #                         # Right before we send the message, clear the menu - this only fails if the message being sent fails
    #                         self._IN_MENU = Menu.NO_MENU
    #                         self.sendMessage(json.dumps(background_selection_msg).encode('utf-8'))
    #
    #                 if self._IN_MENU == Menu.CHARACTER_CREATION_SELECT_WEAPON and not self._SENT_WEAPON_SELECTION:
    #                     if self.config.starting_weapon not in self.weapon_options.keys():
    #                         print(
    #                             "ERROR weapon {} specified in config is not available. Available choices are: {}".format(
    #                                 self.config.starting_weapon, self.weapon_options.keys()))
    #                     else:
    #                         weapon_selection_hotkey = self.weapon_options[self.config.starting_weapon]
    #                         weapon_selection_msg = self.get_hotkey_json_as_msg(weapon_selection_hotkey)
    #                         print("SENDING WEAPON SELECTION MESSAGE OF: {}".format(weapon_selection_msg))
    #                         self._SENT_WEAPON_SELECTION = True
    #                         # Right before we send the message, clear the menu - this only fails if the message being sent fails
    #                         self._IN_MENU = Menu.NO_MENU
    #                         self.sendMessage(json.dumps(weapon_selection_msg).encode('utf-8'))
    #
    #                 if self._PLAYER_DIED and self._IN_MENU == Menu.CHARACTER_INVENTORY_MENU:
    #                     print("SENDING ENTER KEY BECAUSE WE ARE IN THE INVENTORY AFTER DEATH MENU")
    #                     enter_key_msg = {"text": "\r", "msg": "input"}
    #                     self.sendMessage(json.dumps(enter_key_msg).encode('utf-8'))
    #
    #                 if self._IN_MENU in [Menu.NO_MENU, Menu.CHARACTER_INVENTORY_MENU, Menu.CHARACTER_ITEM_SPECIFIC_MENU, Menu.ALL_SPELLS_MENU, Menu.ABILITY_MENU, Menu.SKILL_MENU, Menu.ATTRIBUTE_INCREASE_TEXT_MENU] and self._RECEIVED_MAP_DATA and not self._BEGIN_DELETING_GAME:
    #                     #self.game_state.draw_cell_map()
    #                     # the following executes the next action if we are using an instance of Agent to control
    #                     # sending actions
    #                     if self.agent:
    #                         next_action = self.agent.get_action(self.game_state)
    #                         # If you've gotten to the point of sending actions and a character was not created
    #                         # then delete game if config has always_start_new_game set to True
    #                         if config.WebserverConfig.always_start_new_game and not self._CREATED_A_NEW_CHARACTER:
    #                             self._BEGIN_DELETING_GAME = True
    #                         # elif next_action and isinstance(next_action, MenuChoice):
    #                         #     print("We are about to send menu choice action: {}".format(next_action))
    #                         #     self.sendMessage(json.dumps(Action.get_execution_repr(next_action)).encode('utf-8'))
    #                         #     self.last_message_sent = next_action
    #                         #     self.actions_sent += 1
    #                         elif next_action:
    #                             print("We are about to send action: {}".format(next_action))
    #                             self.sendMessage(json.dumps(Action.get_execution_repr(next_action)).encode('utf-8'))
    #                             self.last_message_sent = next_action
    #                             self.actions_sent += 1
    #                         else:
    #                             raise Exception("next_action is {}".format(next_action))
    #                     else:
    #                         print("Game Connection Does Not Have An Agent")
    #
    #                 # State machine to abandon character and delete the game
    #                 if self._BEGIN_DELETING_GAME and not self._SENT_CTRL_Q_TO_DELETE_GAME:
    #                     # send abandon character and quit game (mimics ctrl-q)
    #                     abandon_message = {"msg": "key", "keycode": 17}
    #                     print("SENDING CTRL-Q TO ABANDON CHARACTER")
    #                     self.sendMessage(json.dumps(abandon_message).encode('utf-8'))
    #                     self._SENT_CTRL_Q_TO_DELETE_GAME = True
    #
    #                 elif self._BEGIN_DELETING_GAME and self._SENT_CTRL_Q_TO_DELETE_GAME and not self._SENT_YES_TEXT_TO_DELETE_GAME:
    #                     # send 'yes' confirmation string
    #                     confirmation_message = {"text": "yes\r", "msg": "input"}
    #                     print("SENDING YES CONFIRMATION TO ABANDON CHARACTER")
    #                     self.sendMessage(json.dumps(confirmation_message).encode('utf-8'))
    #                     self._SENT_YES_TEXT_TO_DELETE_GAME = True
    #
    #                 elif self._BEGIN_DELETING_GAME and self._SENT_YES_TEXT_TO_DELETE_GAME and not self._SENT_ENTER_1_TO_DELETE_GAME:
    #                     # send first enter to clear the menu
    #                     first_enter_msg = {"text": "\r", "msg": "input"}
    #                     print("SENDING FIRST ENTER FOLLOWING TO ABANDON CHARACTER")
    #                     self.sendMessage(json.dumps(first_enter_msg).encode('utf-8'))
    #                     self._SENT_ENTER_1_TO_DELETE_GAME = True
    #
    #                 elif self._BEGIN_DELETING_GAME and self._SENT_ENTER_1_TO_DELETE_GAME and not self._SENT_ENTER_2_TO_DELETE_GAME:
    #                     # send first enter to clear the menu
    #                     second_enter_msg = {"text": "\r", "msg": "input"}
    #                     print("SENDING SECOND ENTER FOLLOWING TO ABANDON CHARACTER")
    #                     self.sendMessage(json.dumps(second_enter_msg).encode('utf-8'))
    #                     self._SENT_ENTER_2_TO_DELETE_GAME = True
    #
    #                 elif self._BEGIN_DELETING_GAME and self._SENT_ENTER_2_TO_DELETE_GAME and not self._SENT_ENTER_3_TO_DELETE_GAME:
    #                     # send first enter to clear the menu
    #                     third_enter_msg = {"text": "\r", "msg": "input"}
    #                     print("SENDING THIRD ENTER FOLLOWING TO ABANDON CHARACTER")
    #                     self.sendMessage(json.dumps(third_enter_msg).encode('utf-8'))
    #                     self._SENT_ENTER_3_TO_DELETE_GAME = True
    #                     self.reset_before_next_game()
    #
    #         print("About to sleep for delay {}".format(config.WebserverConfig.delay))
    #
    #         yield
    #
    #         # self.sleep_task = asyncio.create_task(asyncio.sleep(config.WebserverConfig.delay))
    #         # await self.sleep_task
    #         # self.sleep_task = None
    #
    #         #await asyncio.sleep(config.WebserverConfig.delay)
    #
    #         #print(str(int(time.time())) + "  return from asyncio.sleep()")
    #         times.append(time.time())
    #         if last_saved_time == None:
    #             last_saved_time = time.time()
    #         elif time.time() - last_saved_time > save_time_delay:
    #             with open(time_data_save_dir / ("times" + suffix + ".pkl"), 'ab') as f:
    #                 pickle.dump(times, f)
    #             last_saved_time = time.time()
    #             times = []
    #

    # self.sendMessage(msg) ordinarily would send a message called msg over a websocket,
    # but here we want it to just call self.handle_input(msg), which will end up writing it
    # into the file descriptor of the child process containing the running crawl binary.

    # These two functions handle the output of the agent program and send it into
    # the crawl binary running in the terminal with the file descriptor given by
    # child_fd.

    def handle_input(self, msg):
        # JTS
        # Input commands were sent by the user to this function in json format
        # and they need to be converted into utf8.
        #
        # msg object has fields "data" and "text"

        obj = json_decode(msg)

        if obj["msg"] == "input" and self.process:
            self.last_action_time = time.time()

            data = ""
            for x in obj.get("data", []):
                data += chr(x)

            data += obj.get("text", u"").encode("utf8")

            # JTS
            # self.process is a TerminalRecorder object. This is how input from the player
            # is fed into the crawl program:
            self.process.write_input(data)

        elif obj["msg"] == "force_terminate":
            self._do_force_terminate(obj["answer"])

        elif obj["msg"] == "stop_stale_process_purge":
            self._stop_purging_stale_processes()

        elif self.conn and self.conn.open:
            self.conn.send_message(msg.encode("utf8"))

    def write_input(self, data):
        # JTS
        # self.poll() is polling to see that the process is still ongoing
        # and hasn't terminated. If it is still ongoing self.poll() will
        # return None.
        #if self.poll() is not None: return

        while len(data) > 0:
            # JTS
            # self.child_fd is the file descriptor for the child process
            # forked up in the _spawn() function, and is supposedly now in
            # the middle of running the crawl program using
            # os.execvpe()
            # So this is writing the user's input commands directly into
            # that terminal program.
            logging.debug("[parent] about to write data to child_fd: {}".format(data))
            written = os.write(self.child_fd, data)
            data = data[written:]


if __name__ == "__main__":
    connection = GameConnectionLocal()
    print("Created game connection")
    time.sleep(1)
    print("About to send game play message")
    play_game_msg = {'msg': 'play', 'game_id': 'dcss-web-trunk'}
    #                 self.sendMessage(json.dumps(play_game_msg).encode('utf-8'))
    connection.write_input(json.dumps(play_game_msg).encode('utf-8'))
    print("Sent send game play message")
