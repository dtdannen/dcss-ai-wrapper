"""

Demo of an RL agent on the sonja sprint in crawl 23.1

Make sure to run crawl before running this demo, see:
    start_crawl_terminal_sprint.sh

"""

from game_connection_4 import DCSSProtocol
from agent import SimpleRandomAgent, TestAllCommandsAgent, FastDownwardPlanningAgent
from actions import Command, Action
import config
import asyncio
import logging
import time
import threading
from gamestate import Monster
from autobahn.asyncio.websocket import WebSocketClientFactory

logging.basicConfig(level=logging.INFO)


def main():
    factory = WebSocketClientFactory(config.WebserverConfig.server_uri)
    factory.protocol = DCSSProtocol

    loop = asyncio.get_event_loop()
    coro = loop.create_connection(factory, config.WebserverConfig.server_ip, config.WebserverConfig.server_port)
    loop.run_until_complete(coro)
    loop.run_forever()

    agent = FastDownwardPlanningAgent()

    loop.close()
    #
    # game = GameConnection(config=config.WebserverConfig())
    # asyncio.get_event_loop().run_until_complete(game.connect_webserver())
    # time.sleep(3)
    # asyncio.get_event_loop().run_until_complete(game.login_webserver())
    # time.sleep(3)
    # asyncio.get_event_loop().run_until_complete(game.load_game_on_webserver())
    #
    # print("Ready to start the agent playing")
    # #agent = SimpleRandomAgent()
    # agent = FastDownwardPlanningAgent()
    #
    # print("Waiting 3 seconds....")
    # time.sleep(3)
    #
    # #game.send_and_receive_command_ws(Command.ENTER_KEY)
    #
    # setup_actions = agent.get_game_mode_setup_actions_webserver()
    # i = 0
    # for action in setup_actions:
    #     print("Sending setup action {} with content {}".format(i, action))
    #     asyncio.get_event_loop().run_until_complete(game.send_and_receive_ws(action))
    #     print("Waiting 3 seconds....")
    #     time.sleep(3)
    #     i+=1
    #
    # time.sleep(3)
    #
    # print("About to start playing the game")
    # game_state = game.get_gamestate()
    # i = 0
    # while not game_state.has_agent_died():
    #     #print(game_state.draw_cell_map())
    #     #print("Visible Monsters are:")
    #     #for m_id, mon in Monster.ids_to_monsters.items():
    #     #    if mon.cell and mon.ascii_sym:
    #     #        print("  {} with id {} and symbol {} on cell {}".format(mon.name, m_id, mon.ascii_sym, "{},{}".format(mon.cell.x, mon.cell.y)))
    #     #print("Monsters away from us (or dead) are:")
    #     #for m_id, mon in Monster.ids_to_monsters.items():
    #     #    if mon.cell:
    #     #        pass
    #     #    else:
    #     #        print("  {} with id {} and symbol {}".format(mon.name, m_id, mon.ascii_sym))
    #
    #     next_action = agent.get_action(game_state)
    #     if next_action not in Action.command_to_msg.keys():
    #         print("Action {} is not implemented yet, skipping for now".format(next_action))
    #         continue
    #     if isinstance(agent, FastDownwardPlanningAgent):
    #         next_next_action = "N/A"
    #         if agent.plan:
    #             if len(agent.plan) > 1:
    #                 next_next_action = agent.plan[0]
    #             print("Goal: {}, type={}, Plan length: {}, Next action: {}, Next^2 Action: {}".format(agent.current_goal, agent.current_goal_type, len(agent.plan), next_action, next_next_action))
    #         else:
    #             pass
    #
    #     game.send_and_receive_command_ws(next_action)
    #
    #     game_state = game.get_gamestate()
    #     i += 1
    #
    # if game_state.has_agent_died():
    #     # Quit and delete the game
    #     game.send_and_receive_command_ws(Command.ABANDON_CURRENT_CHARACTER_AND_QUIT_GAME)
    #     game.send_and_receive_command_ws(Command.RESPOND_YES_TO_PROMPT)
    #     game.send_and_receive_command_ws(Command.ENTER_KEY)
    #     game.send_and_receive_command_ws(Command.ENTER_KEY)
    #     game.send_and_receive_command_ws(Command.ENTER_KEY)
    #
    #
    #

if __name__ == "__main__":
    main()

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
