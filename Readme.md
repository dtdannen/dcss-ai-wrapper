# AI Wrapper for Dungeon Crawl Stone Soup

![](contribute/dcss-ai-wrapper-terminal-demo.gif)

(Demo of an agent taking random actions to play DCSS in the terminal)

# About

**dcss-ai-wrapper** aims to create an API for Dungeon Crawl Stone Soup for Artificial Intelligence research. This effort started with the following paper: 

*Dannenhauer, D., Floyd, M., Decker, J., Aha D. W. [Dungeon Crawl Stone Soup as an Evaluation Domain for Artificial Intelligence.](https://arxiv.org/pdf/1902.01769) Workshop on Games and Simulations for Artificial Intelligence. Thirty-Third AAAI Conference on Artificial Intelligence. Honolulu, Hawaii, USA. 2019.*

If you use this repository in your research, please cite the above paper.

If you'd like to contribute to the research effort aligned with this project, see [Research Effort](contribute/ResearchEffort.md)

# Development Community

Join the chat at https://gitter.im/dcss-ai-wrapper/community

# Installation

## Pre-requisites

This guide has been tested on Ubuntu 18.04 LTS and assumes you have the following installed:

- git (sudo apt-get install git)
- python2 (sudo apt-get install python2.7)
- pip2 (sudo apt-get install python-pip)
- python3 (sudo apt-get install python3.6)
- pip3 (sudo apt-get install python3-pip)
- A variety of packages required by Dungeon Crawl Stone Soup
    - sudo apt-get install build-essential libncursesw5-dev bison flex liblua5.1-0-dev libsqlite3-dev libz-dev pkg-config python-yaml libsdl2-image-dev libsdl2-mixer-dev libsdl2-dev libfreetype6-dev libpng-dev ttf-dejavu-core

## Installing Dungeon Crawl Stone Soup

While this API is likely to work with the current dcss master branch, it has been tested with the 23.1 version, which
is the recommended version of crawl to use with this API. We recommend installing a local version of crawl inside this
project's folder.

1. Make sure you have cloned this repository (dcss-ai-wrapper)
    
2. Grab a copy of the 23.1 version of crawl, by cloning the repo and then resetting to the 23.1 version

   `cd ~/dcss-ai-wrapper/`  (assuming this is the directory where you cloned this project - dcss-ai-wrapper)
   
   `git clone https://github.com/crawl/crawl.git`
   
   `cd ~/dcss-ai-wrapper/crawl/`
   
   `git reset --hard d6e21ad81dcba7f7f8c15336e0e985f070ce85fb`
   
   `git submodule update --init`

3. Compile crawl with the following flags

    `cd ~/dcss-ai-wrapper/crawl/crawl-ref/source/`
    
    `sudo make install prefix=/usr/local/ WEBTILES=y`

# How to Run a simple agent in the terminal

1. Open a new terminal, cd into dcss-ai-wrapper/ and run:

    `./start_crawl_terminal_dungeon.sh`

   Note that nothing will happen until an agent connects.
   
   The terminal that runs this command must be a minimum width, so try enlarging the terminal if it doesn't work and you are using a small monitor/screen. (Only try changing the width if the next step fails).

2. Open a new terminal, cd into dcss-ai-wrapper/ and run:

    `python3 main.py`
	    
3. You should now be able to watch the agent in the terminal as this script is running, as shown in the demo gif at the top of this readme.

# Run the fastdownard planning and goalreasoning agent

1. Download and compile the [fastdownward planner](http://www.fast-downward.org/ObtainingAndRunningFastDownward) and put it in a folder under dcss-ai-wrapper so the folder structure looks like this:

    `dcss-ai-wrapper/FastDownward/fast-downward.py`

2. Switch the agent in `main.py` to be the `FastDownwardPlanningAgent` agent, like:

    `agent = FastDownwardPlanningAgent()`

3. Run main.py and it should work. There's a chance that the fastdownward planner will fail to find a plan. Since the dungeon is procedurally generated, try a few times before troubleshooting fastdownward. If you do need to troubleshoot, start by displaying fastdownward's output. This can be done by remove the `stdout=subprocess.DEVNULL` option when calling FastDownward via subprocess.

## Web browser setup (see ISSUE #8)
The following instructions need to be updated - see issue 8.

The following steps enable the API to connect to DCSS running on a webserver on the local host, which means you can watch
your AI agent play DCSS in the tile version that runs in the web browser.

1. Install requirements to run the webserver version of the game

    `sudo pip2 install tornado==3.0.2`
    
    `sudo pip3 install asyncio`
    
    `sudo pip3 install websockets`

2. Test that the browser version of the game is working

    `cd ~/dcss-ai-wrapper/crawl/crawl-ref/source/`
    
    `python2 webserver/server.py` 

     Now open your web browser and go to http://localhost:8080/

     Click register at the top right (not necessary to enter an email).

     Then after logging in, click the leftmost link under "Play now:" which is "DCSS trunk".
     You should then go to a menu where you choose your character configuration (i.e. species > background > weapon)
     Once you proceed through the menus you should find yourself in a newly generated world. If you've reached this
     step (and can see the tiles) you have successfully installed the game.

# Troubleshooting


  Problem: Errors during compiling
  Solution: Double check you installed all the packages listed at the
  beginning that crawl needs. These come from the install instructions
  for crawl itself.

  Problem: No images showing up and getting errors from the webserver like:
    'HTTPOutputError: Tried to write X number of bytes but error with content length'
    
  Solution: Make sure you are using tornado 3.0 (not the version that installs by default)

# Running the webserver
----------

Note these instructions may be outdated - they need to be double checked.

## Start webserver

   `cd crawl_18/crawl/crawl-ref/source/`
   `python2 webserver/server.py`

## now check to see if its up using a browser at localhost:8080

### If this is the first time you are running this on your machine,
  you will need to register an account on the webserver (in the
  browser). Keep track of the username and password, as you will enter
  this into the code file, which the agent will use to connect to the
  server.

## In a new terminal, go back to top level dir 

## run the test_interface script using python3 (sidenote: installing asyncio
  on python2.x will initially work but then you get errors when trying
  to import it)

    `python3 main.py`

# Watching the Agent Play

1. Navigate your browser to localhost:8080

2. You should see a list of agents playing, click on the agent's name to spectate (note, you do not need to log in for this). If you don't see the agent on the list, try refreshing the page.

