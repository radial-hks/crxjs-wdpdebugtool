import asyncio
import websockets

async def echo(websocket):
    async for message in websocket:
        await websocket.send(message)

async def main():
    async with websockets.serve(echo, "localhost", 5151):
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())