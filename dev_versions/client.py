# client.py. This is an early development version of client_menu.py, 
# It is a version of the client with no start menu and options screen,
# and instantly connects to the server-hosted Asteroids game upon running python3 client.py.

import socket
import pickle
import pygame
import gameParameters
from stage import Stage
from ship import Ship
from blackhole import Blackhole

SERVER_ADDR = ("66.228.34.65", 5500)
BUFFER_SIZE = 65536

class Network:
    def __init__(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 65536)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 65536)
        self.s.settimeout(5.0)
        
        self.s.connect(SERVER_ADDR)

        init = self.s.recv(2048).decode()
        if init.startswith("too many"):
            raise RuntimeError(init)
        self.player = int(init)

    def send(self, action):
        self.s.sendall(str(action).encode())
        data = self.s.recv(BUFFER_SIZE)
        if not data:
            raise RuntimeError("Server closed the connection.")
        if data.startswith(b"too many"):
            raise RuntimeError(data.decode())
        return pickle.loads(data)


def main():
    pygame.init()
    WIDTH, HEIGHT = gameParameters.screenWidth, gameParameters.screenHeight

    try:
        net = Network()
    except RuntimeError as e:
        print("Server refused connection:", e)
        return
    print(f"You are player {net.player}")

    # stage setup
    stage = Stage("Asteroids Client", (WIDTH, HEIGHT))

    # create ship sprites
    ships = []
    for i in range(gameParameters.startNumShips):
        ship = Ship(stage, shipIndex=i, color=gameParameters.shipColor[i])
        stage.addSprite(ship.thrustJet)
        stage.addSprite(ship)
        ships.append(ship)

    # create blackhole sprite
    bh_sprite = Blackhole(stage, gameParameters.screenCenter)
    stage.addSprite(bh_sprite)

    clock = pygame.time.Clock()
    run = True
    while run:
        clock.tick(60)

        # get input from the user
        keys = pygame.key.get_pressed()
        action = 0
        if keys[pygame.K_UP]:    action = 1
        elif keys[pygame.K_LEFT]:  action = 2
        elif keys[pygame.K_RIGHT]: action = 3

        # send action, receive state
        try:
            state = net.send(action)
        except RuntimeError as e:
            print("Connection error:", e)
            break

        # update sprite positions
        for idx, s in enumerate(state['ships']):
            ships[idx].position.x = s['x']
            ships[idx].position.y = s['y']
            ships[idx].angle      = s['angle']

        bh = state['blackhole']
        bh_sprite.position.x = bh['x']
        bh_sprite.position.y = bh['y']

        # draw using full game rendering system
        stage.screen.fill((10, 10, 10))
        stage.moveSprites()
        stage.drawSprites()
        pygame.display.flip()

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                run = False

    pygame.quit()

if __name__ == "__main__":
    main()
