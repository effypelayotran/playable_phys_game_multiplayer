import pygame
from pygame.locals import *
import sys
import asyncio
import websockets
import json

from vectorsprites import *
from ship import *
from stage import *
from blackhole import *
import gameParameters

pygame.init()

class Asteroids:
    def __init__(self):
        self.stage = Stage('Spaceship Gravity Game', (gameParameters.screenWidth, gameParameters.screenHeight))
        self.paused = False
        self.showingFPS = True
        self.frameAdvance = False
        self.gameState = "playing"
        self.shipsList = []
        self.shipStates = {}  # ship_id -> position/angle
        self.shipId = None  # ID assigned by server
        self.fps = 0
        self.clock = pygame.time.Clock()

        self.createBlackhole()

    def createBlackhole(self):
        position = gameParameters.screenCenter
        bh = Blackhole(self.stage, position)
        self.stage.addSprite(bh)

    async def websocket_handler(self):
        uri = "wss://asteroids-server.onrender.com"
        try:
            async with websockets.connect(uri) as websocket:
                await websocket.send(json.dumps({"type": "join"}))
                while True:
                    data = await websocket.recv()
                    msg = json.loads(data)
                    if msg["type"] == "init":
                        self.shipId = msg["id"]
                    elif msg["type"] == "state":
                        self.shipStates = msg["ships"]
                    await asyncio.sleep(0)
        except Exception as e:
            print("WebSocket error:", e)

    def drawShips(self):
        self.stage.clearScreen()
        for id, state in self.shipStates.items():
            pos = Vector2d(state["x"], state["y"])
            angle = state["angle"]
            color = gameParameters.shipColor[int(id) % len(gameParameters.shipColor)]
            ship = Ship(self.stage, position=pos, angle=angle, color=color)
            self.stage.addSprite(ship.thrustJet)
            self.stage.addSprite(ship)

    async def game_loop(self):
        frameCount = 0
        timePassed = 0

        while True:
            timePassed += self.clock.tick(60)
            frameCount += 1
            if frameCount % 10 == 0:
                self.fps = round((frameCount / (timePassed / 1000.0)))
                frameCount = 0
                timePassed = 0

            for event in pygame.event.get():
                if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                    sys.exit(0)

            keys = pygame.key.get_pressed()
            if self.shipId is not None:
                if keys[K_LEFT]:
                    await self.send_input("ArrowLeft")
                if keys[K_RIGHT]:
                    await self.send_input("ArrowRight")
                if keys[K_UP]:
                    await self.send_input("ArrowUp")

            self.drawShips()
            pygame.display.flip()
            await asyncio.sleep(0)

    async def send_input(self, key):
        try:
            async with websockets.connect("wss://asteroids-server.onrender.com") as websocket:
                await websocket.send(json.dumps({"type": "input", "key": key}))
        except:
            pass


async def main():
    game = Asteroids()
    await asyncio.gather(game.websocket_handler(), game.game_loop())

__import__('asyncio').run(main())