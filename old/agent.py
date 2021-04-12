import re
class Action:

    def __init__(self,name:str,msg:{},args:[]=[]):
        self.name = name
        self.msg = msg
        self.args = args

    def _ash__(self):
        return hash(self.name)

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return self.name

    def get_json(self):
        return self.msg


class CrawlAIAgent:

    def game_mode_selection(self):
        raise NotImplementedError("An agent must implement game mode selection function which determines which game"
                                  " mode (e.g., crawl, sprint, tutorial, etc) it is designed for")

    def species_selection(self):
        raise NotImplementedError("An agent must implement species selection function which determines the species"
                                  " (e.g., minotuar, vampire, etc)  of the character in the game")

    def background_selection(self):
        raise NotImplementedError("An agent must implement background selection function which determines the DCSS"
                                  " background (e.g., fighter, berserker, etc")

    def weapon_selection(self):
        raise NotImplementedError("An agent must iready_to_permemantly_end_gamemplement weapon selection function which determines the DCSS"
                                  " weapon to start with (e.g., spear, hand axe, etc")

    def next_action(self):
        raise NotImplementedError("An agent must implement next_action() so that it will return an action to the game")

    def add_server_message(self,json_msg:{}):
        raise NotImplementedError("An agent must implement add_server_message which takes the most recent server"
                                  " message. This message is mostly used to ensure the agent has a current states of"
                                  " the game")

    def ready_to_delete_game(self):
        raise NotImplementedError("An agent must implement ready_to_delete_game() which denotes when the agent should"
                                  " quit and delete the game")

    def create_input_action(text):
        for a in CrawlAIAgent.all_actions:
            if a.get_json()['msg'] == 'input' and a.get_json()['text'] == text:
                return a

        return Action('undefined', {'msg': 'input', 'text': text})


    loc={'x':None,'y':None}
    # movement
    _move_N_h = Action('north_h', {'msg': 'key', 'keycode': -254})
    _move_S_h = Action('south_h', {'msg': 'key', 'keycode': -253})
    _move_E_h = Action('east_h', {'msg': 'key', 'keycode': -251})
    _move_W_h = Action('west_h', {'msg': 'key', 'keycode': -252})
    _move_NW_h = Action('northwest_h', {'msg': 'key', 'keycode': -1007})
    _move_SW_h = Action('southwest_h', {'msg': 'key', 'keycode': -1001})
    _move_SE_h = Action('southeast_h', {'msg': 'key', 'keycode': -1003})
    _move_NE_h = Action('northeast_h', {'msg': 'key', 'keycode': -1009})

    # text actions
    _respond_no = Action('no', {'msg': 'input', 'text': 'N'})
    _go_up = Action('up', {'msg': 'input', 'text': '<'})

    _get_item = Action('get', {'msg': 'input', 'text': 'g'})
    _drop_item = Action('drop', {'msg': 'input', 'text': 'd'})
    _eat = Action('eat', {'msg': 'input', 'text': 'e'})

    _enter_throw = Action ('enter_throw', {'msg': 'input', 'text': 'f'})
    _aim_west = Action('aim_west', {'msg': 'key', 'keycode': -252})
    _aim_east = Action('aim_east', {'msg': 'key', 'keycode': -251})
    _aim_north = Action('aim_north', {'msg': 'key', 'keycode': -254})
    _aim_south = Action('aim_south', {'msg': 'key', 'keycode': -253})
    _throw_stop = Action ('throw', {'msg': 'input', 'text': '.'})

    _open_door = Action ('open_door', {'msg': 'input', 'text': 'O'})
    _close_door = Action ('close_door', {'msg': 'input', 'text': 'C'})

    def _check(self, diff_x, diff_y):
        x=self.game_state.map_obj_player_x
        y=self.game_state.map_obj_player_y
        new_x=str(x+diff_x)
        new_y=str(y+diff_y)
        new_cell=None
        ats=[]
        doors=[]
        mons=[]
        for atom in self.game_state.get_asp_str().split(".\n"):
            atom_parts = re.split("\(|\)", atom)
            if atom_parts[0]=="at":
                args=atom_parts[1].split(",")
                if args[1]==new_x and args[2]==new_y:
                    new_cell=args[0]
            if atom_parts[0] == "closed_door":
                doors.append(atom_parts[1])
        for door in doors:
            if door==new_cell:
                #can't move
                return False
        return True

    def _build_move_N(self):
        if self._check(0,-1):
            return [self._move_N_h]
        else:
            return []
    def _build_move_S(self):
        if self._check(0,1):
            return [self._move_S_h]
        else:
            return []
    def _build_move_E(self):
        if self._check(1,0):
            return [self._move_E_h]
        else:
            return []
    def _build_move_W(self):
        if self._check(-1,0):
            return [self._move_W_h]
        else:
            return []
    def _build_move_NW(self):
        if self._check(-1,-1):
            return [self._move_NW_h]
        else:
            return []
    def _build_move_SW(self):
        if self._check(-1,1):
            return [self._move_SW_h]
        else:
            return []
    def _build_move_SE(self):
        if self._check(1,1):
            return [self._move_SE_h]
        else:
            return []
    def _build_move_NE(self):
        if self._check(1,-1):
            return [self._move_NE_h]
        else:
            return []

    _move_N = Action('north',{'func': _build_move_N})
    _move_S = Action('south',{'func': _build_move_S})
    _move_E = Action('east',{'func': _build_move_E})
    _move_W = Action('west',{'func': _build_move_W})
    _move_NW = Action('northwest', {'func': _build_move_NW})
    _move_SW = Action('southwest',{'func': _build_move_SW})
    _move_SE = Action('southeast',{'func': _build_move_SE})
    _move_NE = Action('northeast',{'func': _build_move_NE})

    def _build_throw(self,x: int,y: int):  #Need to add item arg.
        print(x,y)
        throw=[]
        throw.append(self._enter_throw)
        target=self.loc
        while x<target['x']:
            throw.append(self._aim_west)
            target['x']-=1
        while x>target['x']:
            throw.append(self._aim_east)
            target['x']+=1
        while y<target['y']:
            throw.append(self._aim_north)
            target['y']-=1
        while y>target['y']:
            throw.append(self._aim_south)
            target['y']+=1
        throw.append(self._throw_stop)
        return throw
    _throw = Action('throw', {'func': _build_throw})

    cardinal_move_actions = [_move_N,
                             _move_S,
                             _move_E,
                             _move_W,
                             _move_NW,
                             _move_NE,
                             _move_SW,
                             _move_SE]

    item_actions = [_get_item]#, _drop_item, _eat]
    throw_actions = [_throw]

    move_actions = [_move_N,
                    _move_S,
                    _move_E,
                    _move_W,
                    _move_NW,
                    _move_NE,
                    _move_SW,
                    _move_SE]
    door_actions = [_open_door]
    all_actions = cardinal_move_actions+door_actions


    # menu escape
    _exit_via_esc = {'msg': 'key', 'keycode': 27}

    # # combat other than movement
    # key_actions['tab_auto_attack'] = {'msg': 'key', 'keycode': 9}
    #
    # # End key_actions
    #
    # '''
    # Text actions have multiple uses, and are only concerned what
    # letter will be sent to the webserver. For example, a Berserker can
    # press 'a' to open up the abilities menu and then press 'a' again to
    # activate Berserk mode. The same 'a' has many different uses (by default, 'a' opens the special ability menu; however when the user opens the inventory, 'a' corresponds to a specific item in the inventory).
    #
    # '''
    #
    # text_actions = {}
    #
    # # pickup an item in current location
    # text_actions['g'] = {'text': 'g', 'msg': 'input'}
    #
    # # auto explore command
    # text_actions['o'] = {'text': 'o', 'msg': 'input'}
    #
    # # access abilities
    # text_actions['a'] = {'text': 'a', 'msg': 'input'}
    #
    # # inventory
    # text_actions['i'] = {'text': 'i', 'msg': 'input'}
    #
    # # wait
    # text_actions['5'] = {'text': '5', 'msg': 'input'}
    #
    # # eat
    # text_actions['e'] = {'text': 'e', 'msg': 'input'}
    #
    # # exit up
    # text_actions['<'] = {'text': '<', 'msg': 'input'}
    #
    # # enter key for clearing game text messages
    # key_actions['enter_key'] = {'text': '\r', 'msg': 'input'}
    #
