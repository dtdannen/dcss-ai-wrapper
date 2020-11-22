"""

Demo of an RL agent on the sonja sprint in crawl 23.1

Make sure to run crawl before running this demo, see:
    start_crawl_terminal_sprint.sh

"""

from game_connection import GameConnection
from agent import SimpleRandomAgent, TestAllCommandsAgent, FastDownwardPlanningAgent
from actions import Command, Action
import config
import asyncio

def main():
    game = GameConnection(config=config.WebserverConfig())
    asyncio.get_event_loop().run_until_complete(game.connect_webserver())
    print("\n\nconnected!\n\n")
    agent = SimpleRandomAgent()
    #agent = FastDownwardPlanningAgent()

    setup_actions = agent.get_game_mode_setup_actions()
    for action in setup_actions:
        print("\n\nexecution action {}\n\n".format(action))
        asyncio.get_event_loop().run_until_complete(game.send_and_receive_dict_ws(action))

    print("\n\nAbout to start playing the game \n\n")
    game_state = game.get_gamestate()
    i = 0
    while not game_state.has_agent_died():
        #print(game_state.draw_cell_map())

        next_action = agent.get_action(game_state)
        if next_action not in Action.command_to_msg.keys():
            print("Action {} is not implemented yet, skipping for now".format(next_action))
            continue

        asyncio.get_event_loop().run_until_complete(game.send_and_receive_command_ws(next_action))
        game_state = game.get_gamestate()
        i+=1

    if game_state.has_agent_died():
        # Quit and delete the game
        game.send_and_receive_command(Command.ABANDON_CURRENT_CHARACTER_AND_QUIT_GAME)
        game.send_and_receive_command(Command.RESPOND_YES_TO_PROMPT)
        game.send_and_receive_command(Command.ENTER_KEY)
        game.send_and_receive_command(Command.ENTER_KEY)
        game.send_and_receive_command(Command.ENTER_KEY)

    game.close()

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
