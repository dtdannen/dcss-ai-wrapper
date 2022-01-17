# Roadmap to Version 1.0 

The following is a tentative roadmap for the project to reach version 1.0.

### v0.1
*  ~~Sprint game mode is supported~~
*  ~~Items in cells can be parsed by the game state~~
*  API for vector state representations is complete
*  API for PDDL state representations is complete
*  Update `models/fastdownward_simple.pddl` to be consistent with PDDL state representation API
*  ~~New agent class that acts as a passthrough for a human player to play the game~~ 

### v0.2 
*  Create simple RL agent that uses vector-based API
*  Create simple planning agent that uses PDDL-based API 

### v0.3
*  Add support for autobahn for terminal version of the game
*  Refactor game connection code to be less redundant between browser and terminal versions of the game
*  Ensure all game modes are supported in the terminal version running on linux

### v0.4
*  Add metrics for measuring API performance (speed of actions being sent to game, etc.)
*  Add metrics for measuring agent performance (number of tiles visited, experience level, number of monsters killed, etc.)

### v0.5
*  Add player skills into the gamestate data
*  Add actions to change experience point allocation for skills 

### v0.6 
*  Enable agent to receive spectator commands through spectator chat, including 'pause' and 'resume'

### v0.7
*  ~~Refactor code into a pip installable library~~

### v0.8
*  Code refactoring to adhere to better design principles

### v 0.9
*  Replace most print statements with logging statements
*  Log files separated into agent logs and network logs

### v 1.0
*  Documentation of all functions
*  Documentation hosted on pypi packages page
 
