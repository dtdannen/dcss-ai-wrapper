import asyncio
import zlib
import websockets
import json

async def query_server(websocket):
    '''
    I want to get all data from the server until the server is empty (i.e. nothing else left to get)
    and then I want to hand control over to the agent to send an action
    '''

    while True:
        print("querying server")
        data_recv = await websocket.recv()
        data_recv += bytes([0, 0, 255, 255])
        json_message = decomp.decompress(data_recv)
        json_message = json_message.decode("utf-8")

        msg_from_server = json.loads(json_message)

    # do work

    # now say you can hand over
    await send_agent_actions()

    # then when it returns, execution will be here


async def send_agent_actions():
    delay = 1
    while True:

        pass

async def startup(server_uri):
    ws = await websockets.connect(server_uri)
    return ws

if __name__ == "__main__":

    server_uri = 'ws://localhost:8080/socket'

    ### CHANGE USERNAME AND PASSWORD HERE ###
    login_msg = {'msg': 'login',
                 'username': 'midca',
                 'password': 'midca'}

    decomp = zlib.decompressobj(-zlib.MAX_WBITS)

    ws = startup(server_uri)