*****************
Creating an Agent
*****************

Creating an agent is as simple as subclassing the BaseAgent class. The most important part is to override the
``get_action()`` function, which is where you obtain the game state object. The return value of the function will be the
next action that gets executed by the dcss-ai-wrapper API in the current game of DCSS that the agent is playing.

.. literalinclude:: ../../src/dcss/agent/randomagent.py
    :linenos:
    :language: python
    :lines: 1-4, 8-9, 11-22

And then to run the agent, you need to create a WebSockGame object with the agent class, like this:

.. literalinclude:: ../../src/dcss/agent/randomagent.py
    :linenos:
    :language: python
    :lines: 5-7, 25-34


The full example can be found in **src/dcss/agent/randomagent.py**:

.. literalinclude:: ../../src/dcss/agent/randomagent.py
    :linenos:
    :language: python
    :lines: 1-34

=========
Moving On
=========

Next we look at the state representations available from the ``GameState`` object.
