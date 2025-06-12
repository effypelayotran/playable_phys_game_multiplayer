# playable_phys_game_multiplayer

## This repo is built directly of the previous ```playable_phys_game``` Github Repo, with the addition of
1. ```asteroids_compatible.py``` -> A multiplayer compatible version of asteroids.py. Defines the Asteroids class.
2. ```game.py```-> Store an instance of the Asteroids Game. Has helper function ```get_state``` which returns the current state of the Asteroids game.
2. ```client_menu.py``` -> What the client will render. Sends user actions to the Network, and receives a state (containing the x,y positions of the ships and blackhole) in response  and will draw said  ships and blackhole based on those received x,y coordinates.
3. ```server.py``` -> Starts the Server and listens for new clients. Each new client will have its own thread. The server also handles all the game physics by calling game.step() which calls on self.env.update() which calls on the def update(self) function defined in the Asteroids class in asteroids_compatible.py, and this update(self) function calls of the Asteroids class calls on self.stage.moveSprites() which calls on sprite.move() function for each sprite.
```
def move(self):
    VectorSprite.move(self)
    self.applyBlackholeGravity() # ASSUME SINGLE TICK OF TIME 
    self.applyOtherShipsGravity() # ASSUME SINGLE TICK OF TIME
    self.decreaseThrust() # Currently disabled
```


to support multiplayer play.

## How to Run Locally
1. In ```server.py```, change the address to 127.0.0.1 which is your local computer address. 
2. Then, run ```python3 server.py``` on a terminal window and await the `Server started on 127.0.0.1:5600` message.
3. In ```client_menu.py```, also change the address to 127.0.0.1 and make sure the port matches whatever port number you had set for the server.
4. A pygame window of the Asteorids game should popup. Select START, your desired options, and CONNECT.

## How to Run Live Server, Linode




