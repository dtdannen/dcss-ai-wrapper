*********************
State Representations
*********************

dcss-ai-wrapper offers multiple state representations to support multiple types of AI agents.


Vector-based Representations
############################

Vector-based representations are available as a python list data type containing values where the index of the list
corresponds to the feature. The complete specification is listed below, per category of data describing the state
(i.e. player stats, map data, etc.).


    * `Player stats (vector)`_
    * `Player inventory (vector)`_
    * `Player spells (vector)`_
    * `Player abilities (vector)`_
    * `Player skills (vector)`_
    * `Map data Line-of-Sight (LOS) (vector)`_
    * `Map data current level (vector)`_
    * `Map data all (vector)`_


PDDL-based Representations
############################

Planning Domain Definition Language (PDDL) is a relational, symbolic logic state representation. The following state data
is available via functions that return a set of PDDL facts, that are aligned with the PDDL domain file found under
``models/fastdownward_simple.pddl``.

    * `Player stats (PDDL)`_
    * `Player inventory (PDDL)`_
    * `Player skills (PDDL)`_
    * `Map data Line-of-Sight (LOS) (PDDL)`_
    * `Map data current level (PDDL)`_
    * `Map data all (PDDL)`_
    * `Static Background Knowledge (PDDL)`_

API: Vector-based Representations
#################################


Player stats (vector)
**********************
.. autoapifunction:: src.dcss.state.game.GameState.get_player_stats_vector

Player inventory (vector)
**********************
.. autoapifunction:: src.dcss.state.game.GameState.get_player_inventory_vector

Player spells (vector)
**********************
.. autoapifunction:: src.dcss.state.game.GameState.get_player_spells_vector

Player abilities (vector)
**********************
.. autoapifunction:: src.dcss.state.game.GameState.get_player_abilities_vector

Player skills (vector)
**********************
.. autoapifunction:: src.dcss.state.game.GameState.get_player_skills_vector

Map data Line-of-Sight (LOS) (vector)
**********************
.. autoapifunction:: src.dcss.state.game.GameState.get_egocentric_LOS_map_data_vector

Map data current level (vector)
**********************
.. autoapifunction:: src.dcss.state.game.GameState.get_egocentric_level_map_data_vector

Map data all (vector)
**********************
.. autoapifunction:: src.dcss.state.game.GameState.get_all_map_data_vector


API: PDDL-based Representations
#################################

Player stats (PDDL)
**********************
.. autoapifunction:: src.dcss.state.game.GameState.get_player_stats_pddl


Player inventory (PDDL)
**********************
.. autoapifunction:: src.dcss.state.game.GameState.get_player_inventory_pddl

Player skills (PDDL)
**********************
.. autoapifunction:: src.dcss.state.game.GameState.get_player_skills_pddl

Map data Line-of-Sight (LOS) (PDDL)
**********************
.. autoapifunction:: src.dcss.state.game.GameState.get_egocentric_LOS_map_data_pddl

Map data current level (PDDL)
**********************
.. autoapifunction:: src.dcss.state.game.GameState.get_egocentric_level_map_data_pddl

Map data all (PDDL)
**********************
.. autoapifunction:: src.dcss.state.game.GameState.get_all_map_data_pddl

Static Background Knowledge (PDDL)
**********************
.. autoapifunction:: src.dcss.state.game.GameState.get_background_pddl







