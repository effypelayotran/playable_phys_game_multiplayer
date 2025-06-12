# playable_phys_game_multiplayer

## This repo is built directly of the previous ```playable_phys_game``` Github Repo, with the addition of
1. ```asteroids_compatible.py``` -> A multiplayer compatible version of asteroids.py. Defines the Asteroids class.
2. ```game.py```-> Store an instance of the Asteroids Game. Has helper function ```get_state``` which returns the current state of the Asteroids game.
2. ```client.py``` -> What the client will render. Sends user actions to the Network, and receives a state (containing the x,y positions of the ships and blackhole) in response  and will draw said  ships and blackhole based on those received x,y coordinates.
3. ```server.py``` -> Starts the Server and listens for new clients. Each new client will have its own thread. The server also handles all the game physics by calling game.step() which calls on self.env.update() which calls on the def update(self) function defined in the Asteroids class in asteroids_compatible.py, and this update(self) function calls of the Asteroids class calls on self.stage.moveSprites() which calls on sprite.move() function for each sprite.
```
def move(self):
    VectorSprite.move(self)
    self.applyBlackholeGravity() # ASSUME SINGLE TICK OF TIME 
    self.applyOtherShipsGravity() # ASSUME SINGLE TICK OF TIME
    self.decreaseThrust() # Currently disabled
```


to support multiplayer play.

## How to Run and Test Multiplayer Functionality Locally
1. In ```server.py```, change the address to 127.0.0.1 which is your local computer address. 
2. Then, run ```python3 server.py``` on a terminal window and await the `Server started on 127.0.0.1:5600` message.
3. In ```client.py```, also change the address to 127.0.0.1 and make sure the port matches whatever port number you had set for the server.
4. A pygame window of the Asteorids game should popup. Select START, your desired options, and CONNECT.

## How to Run on Linode (Actual Server)

### How to Start the Server
On the server side, we’re going to be running `python3 server.py` on a Linode SSH connection
Make sure the in the repo, the server address is ("0.0.0.0", 5500) and the client address is ("Public IP Address for your Linode", 5500)
Open a Terminal on your computer.
ssh root@45.79.130.19 (or ssh root@ whatever Public IP Address is listed for your Linode.)
Enter password brownsmli#12025!
Git clone the playble_phys_game_multiplayer repo
Run `screen -ls` to see any currently active screens
Run `screen -S Asteroids`. Then run `sudo apt update
sudo apt install python3-pip python3-pygame` to install dependencies.
Run `cd the playable_phys_game_multiplayer`. Then, run `python3 server.py` . Await the ‘Server started’Mmessage
`Ctrl A+D` if you want to close the screen but not to detach the screen.
Run `screen -S 3672 -X quit` if you want to actually to kill server(but 3672 is replaced with actual ID you see in screen -ls)
To get an ssh root@xx.xx.xx.xx address
Sign up for Linode
Click Create+ (blue button) on Linode with the $5/mo Shared CPU plan
Once created, you’ll find the address listed under Public IP Addresses.

### How to Connect to the Server as a Client
On the client side, make the executable of client.py
pyinstaller --onefile --windowed --add-data "assets/Hyperspace.otf” client.py
 or run `python3 client.py` in the terminal

## Future Development 
Press `r` or a simple keyboard shortcut to Restart Game on the Server-Side. 
Automatically have the game restart after 10 minutes, or after a Win/Loss state has been reached.
Add Win/Loss states.
The second, third, fourth, etc. player that joins can click those Number of Player? Growing Blackhole? Options Buttons but they currently don’t do anything in terms of changing the game that the 1st player that joined and made the game did. Somehow update so that the second, third, fourth etc. player that joins can join an existing game immediately without seeing those options buttons OR start a new game,
On the same not as above, handle Multiple games on the same Server. Add ‘Waiting Room’ of softs.
Add RL Ship (use the get_state as the model input side, model output is either increaseThrust, turnLeft, or turnRight)


## Note on Getting Asteroids on the Web
If we want to get the client to connect to the pygame via a website instead of opening this python executable, you’ll need to use pygbag to convert the client-side version of the pygame into web assembly. (Or use some other new library that can do this?) (Or potentially rewrite the game in Javascript, but this options does not make as much sense given that all the RL training is done in python, and we want to keep the RL and the game compatible.) 




