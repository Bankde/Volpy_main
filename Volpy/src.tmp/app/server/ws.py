#!/usr/bin/env python

import asyncio
import json
from enum import Enum
import websockets

class MsgType(Enum):
    INIT = 0

    WS_DATA = 11                    # For websocket data
    WS_HEARTBEAT_REQ = 12           # For driver-node heartbeat
    WS_HEARTBEAT_RES = 13

    SDP_OFFER = 21
    SDP_ANSWER = 22
    ICE_CANDIDATE = 23
    WEBRTC_DATA = 24                # P2P data
    WEBRTC_HEARTBEAT_REQ = 25       # P2P heartbeat
    WEBRTC_HEARTBEAT_RES = 26

uuid2id = {}
id2connection = {}

async def handler(websocket):
    # Initialize the connection / Any auth goes here
    
    # For every message
    async for message in websocket:
        event = json.loads(message)
        match event["MsgType"]:
            case MsgType.INIT:
                # Response with new ID
                uuid = event["uuid"]
                if uuid in uuid2id:
                    event["id"] = uuid2id(uuid)
                    await websocket.send(json.dumps(event))
                else:
                    # Generate id for node
                    id = str(len(id2connection))
                    uuid2id[uuid] = id
                    id2connection[id] = websocket
                    event["id"] = id
                    await websocket.send(json.dumps(event))

            case MsgType.SEND_DATA | \
                    MsgType.SDP_OFFER | \
                    MsgType.SDP_ANSWER | \
                    MsgType.ICE_CANDIDATE:
                # Just route it
                uuid = event["uuid"]
                id = uuid2id[uuid]
                conn = id2connection[id]
                await conn.send(json.dumps(event))

            case _:
                raise TypeError(f'Unknown message: {event}')
            

            


async def main():
    async with websockets.serve(handler, "", 8001):
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())