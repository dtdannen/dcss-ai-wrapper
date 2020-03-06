'''
This file contains messages for key actions and text inputs to be
sent to webserver, including:
* moving around
* accessing the inventory 
* using items 
* ... etc


These keycodes were identified manually be testing commands using
Chrome's develop tools and observing the communications sent through
the websockets.

'''

# key is a text description of the action
# value is the exact dict that will be sent to the server as JSON

key_actions = {}

# movement
key_actions['move_N'] = {'msg':'key',"keycode":-254}
key_actions['move_S'] = {'msg':'key',"keycode":-253}
key_actions['move_E'] = {'msg':'key',"keycode":-251}
key_actions['move_W'] = {'msg':'key',"keycode":-252}
key_actions['move_NW'] = {'msg':'key',"keycode":-1007}
key_actions['move_SW'] = {'msg':'key',"keycode":-1001}
key_actions['move_SE'] = {'msg':'key',"keycode":-1003}
key_actions['move_NE'] = {'msg':'key',"keycode":-1009}

# menu escape
key_actions['exit_via_esc'] = {'msg':'key','keycode':27}

# combat other than movement
key_actions['tab_auto_attack'] = {'msg':'key', 'keycode':9}

# show history of messages
key_actions['show_previous_messages'] = {'msg':'key', 'keycode':16}

# End key_actions

'''
Text actions have multiple uses, and are only concerned what
letter will be sent to the webserver. For example, a Berserker can
press 'a' to open up the abilities menu and then press 'a' again to
activate Berserk mode. The same 'a' has many different uses (by default, 'a' opens the special ability menu; however when the user opens the inventory, 'a' corresponds to a specific item in the inventory).

'''

text_actions = {}

# pickup an item in current location
text_actions['g'] = {'text':'g', 'msg':'input'}

# auto explore command
text_actions['o'] = {'text':'o', 'msg':'input'}

# access abilities
text_actions['a'] = {'text':'a', 'msg':'input'}

# inventory
text_actions['i'] = {'text':'i', 'msg':'input'}

# wait
text_actions['5'] = {'text':'5', 'msg':'input'}

# eat
text_actions['e'] = {'text':'e', 'msg':'input'}

# exit up
text_actions['<'] = {'text':'<', 'msg':'input'}

# yes
text_actions['y'] = {'text':'Y', 'msg':'input'}

# no
text_actions['n'] = {'text':'N', 'msg':'input'}

# enter key for clearing game text messages
key_actions['enter_key'] = {'text':'\r', 'msg':'input'}

# quaff
text_actions['q'] = {'text':'q', 'msg':'input'}
