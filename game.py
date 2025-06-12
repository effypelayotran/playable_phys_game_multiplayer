import gameParameters
from asteroids_compatible import Asteroids

class Game:
    def __init__(self, id, num_ships=5):
        self.id = id
        if num_ships is not None:
            self.actions = [0] * num_ships 
        else:
            self.actions = [0] * gameParameters.startNumShips         # one action slot per ship
        self.ready = False
        self.env = Asteroids(owner=self, num_ships=num_ships)

    def play(self, player, action):
        # store last action for that player
        self.actions[player] = action

    def step(self):
        # apply each player's stored action to their ship
        for pid, act in enumerate(self.actions):

            ship = self.env.shipsList[pid]
            ship.thrustJet.accelerating = False
            if act == 1:
                ship.increaseThrust()
                ship.thrustJet.accelerating = True
            elif act == 2:
                ship.rotateLeft()
            elif act == 3:
                ship.rotateRight()

        # advance physics one tick
        self.env.update()

    def get_state(self):
        # snapshot of ships + blackhole
        ships = []
        for ship in self.env.shipsList:
            ships.append({
                "x": ship.position.x,
                "y": ship.position.y,
                "angle": ship.angle,
                "color": ship.color
            })

        bh = self.env.blackholeList[0]

        return {
            "ships": ships,
            "blackhole": {
                "x": bh.position.x,
                "y": bh.position.y,
                "radius": bh.radius
            }
        }
