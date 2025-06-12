import os
os.environ["SDL_VIDEODRIVER"] = "dummy"
import pygame
from pygame.locals import *
import sys
import random
import math

from vectorsprites import *
from ship import *
from stage import *
from blackhole import *
from soundManager import *
import gameParameters

class Asteroids:
    def __init__(self, owner=None, num_ships=3):
        """
        owner: if passed (Game), run in headless mode (no display) for server;
        otherwise standalone pygame mode.
        """
        self.owner = owner
        pygame.init()

        # choose display mode based on ownder
        if owner:
            # headless: tiny hidden window for server play
            pygame.display.set_mode((1,1), pygame.HIDDEN)
            self.stage = Stage('ServerSide', (gameParameters.screenWidth, gameParameters.screenHeight))
        else:
            # full display for local play
            self.stage = Stage('Spaceship Gravity Game',
                               (gameParameters.screenWidth, gameParameters.screenHeight))
            self.screen = self.stage.screen
            initSoundManager()

        self.paused = False
        self.showingFPS = True
        self.frameAdvance = False
        self.blackholeList = []
        self.createBlackhole(1)

        self.secondsCount = 1
        self.score = 0
        self.ship = None
        self.shipsNum = 0
        self.num_ships = num_ships
        self.initialiseGame(num_ships)

    def initialiseGame(self, num_ships=None):
        self.gameState = 'playing'
        if num_ships is not None:
            self.startNumShips = num_ships
        else: 
            self.startNumShips = gameParameters.startNumShips
        self.createShipsList()
        self.blackholeList = [] 

        self.numBlackhole = 1 # For game
        self.createBlackhole(self.numBlackhole)
        self.secondsCount = 1
        self.score = 0

    def createShipsList(self):
        self.shipsNum = 0
        self.shipsList = []
        for _ in range(0, self.startNumShips):
            self.addShip()

    def addShip(self):
        self.shipsNum += 1
        idx = self.shipsNum - 1
        color = gameParameters.shipColor[idx] if idx < len(gameParameters.shipColor) else None
        ship = Ship(self.stage, shipIndex=idx, color=color)
        self.stage.addSprite(ship.thrustJet)
        self.stage.addSprite(ship)
        self.shipsList.append(ship)

    def createBlackhole(self, numBlackhole):
        for _ in range(numBlackhole):
            position = gameParameters.screenCenter
            newBlackhole = Blackhole(self.stage, position)
            self.stage.addSprite(newBlackhole)
            self.blackholeList.append(newBlackhole)

    def update(self):
        """New Function Added For Server-Client setup: Advance physics one tick (headless or with drawing)."""
        # move sprites based on velocity/forces
        self.stage.moveSprites()

        # in non-headless, draw to screen
        if not self.owner:
            self.stage.screen.fill((10,10,10))
            self.stage.drawSprites()


    # -------------------------------------------------------------------------
    # Helper methods for local interactive play
    def playGame(self):
        clock = pygame.time.Clock()
        frameCount = 0
        timePassed = 0
        self.fps = 0

        while True:
            timePassed += clock.tick(60)
            frameCount += 1
            if frameCount % 10 == 0:
                self.fps = round(frameCount / (timePassed/1000.0))
                timePassed = 0
                frameCount = 0

            self.input(pygame.event.get())
            if self.paused and not self.frameAdvance:
                self.displayPaused()
                continue

            gameParameters.shipPositions = [s.position for s in self.shipsList]
            self.stage.screen.fill((10,10,10))
            self.stage.moveSprites()
            self.stage.drawSprites()
            self.displayScore()
            if self.showingFPS:
                self.displayFps()
            if self.gameState == 'playing':
                self.playing()
            elif self.gameState == 'exploding':
                self.exploding()
            else:
                self.displayText()
            pygame.display.flip()

    def playing(self):
        if self.shipsNum == 0:
            self.gameState = 'attract_mode'
        else:
            self.processKeys()

    def displayText(self):
        font1 = pygame.font.Font('assets/Hyperspace.otf', 50)
        font2 = pygame.font.Font('assets/Hyperspace.otf', 20)
        font3 = pygame.font.Font('assets/Hyperspace.otf', 30)

        titleText = font1.render('Asteroids', True, (180, 180, 180))
        titleTextRect = titleText.get_rect(centerx=self.stage.width/2)
        titleTextRect.y = self.stage.height/2 - titleTextRect.height*2
        self.stage.screen.blit(titleText, titleTextRect)

        keysText = font2.render('(C) 1979 Atari INC.', True, (255, 255, 255))
        keysTextRect = keysText.get_rect(centerx=self.stage.width/2)
        keysTextRect.y = self.stage.height - keysTextRect.height - 20
        self.stage.screen.blit(keysText, keysTextRect)

        instructionText = font3.render('Press start to Play', True, (200, 200, 200))
        instructionTextRect = instructionText.get_rect(centerx=self.stage.width/2)
        instructionTextRect.y = self.stage.height/2 - instructionTextRect.height
        self.stage.screen.blit(instructionText, instructionTextRect)

    def displayScore(self):
        font1 = pygame.font.Font('assets/Hyperspace.otf', 30)
        scoreStr = f"{self.score:02d}"
        scoreText = font1.render(scoreStr, True, (200, 200, 200))
        scoreTextRect = scoreText.get_rect(centerx=100, centery=45)
        self.stage.screen.blit(scoreText, scoreTextRect)

    def displayPaused(self):
        if self.paused:
            font1 = pygame.font.Font('assets/Hyperspace.otf', 30)
            pausedText = font1.render("Paused", True, (255, 255, 255))
            textRect = pausedText.get_rect(centerx=self.stage.width/2, centery=self.stage.height/2)
            self.stage.screen.blit(pausedText, textRect)
            pygame.display.update()

    def input(self, events):
        self.frameAdvance = False
        for event in events:
            if event.type == QUIT:
                sys.exit(0)
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    sys.exit(0)
                if self.gameState == 'attract_mode' and event.key == K_RETURN:
                    self.initialiseGame()
                if event.key == K_p:
                    self.paused = not self.paused
                if event.key == K_r:
                    self.showingFPS = not self.showingFPS
            elif event.type == KEYUP and event.key == K_o:
                self.frameAdvance = True

    def processKeys(self):
        keys = pygame.key.get_pressed()
        for i in range(min(len(gameParameters.shipKeySteering), len(self.shipsList))):
            left, right, thrust = gameParameters.shipKeySteering[i]
            ship = self.shipsList[i]
            if keys[left]: ship.rotateLeft()
            elif keys[right]: ship.rotateRight()
            if keys[thrust]:
                ship.increaseThrust()
                ship.thrustJet.accelerating = True
            else:
                ship.thrustJet.accelerating = False

    def displayFps(self):
        font2 = pygame.font.Font('assets/Hyperspace.otf', 15)
        fpsText = font2.render(f"{self.fps} FPS", True, (255, 255, 255))
        fpsRect = fpsText.get_rect(centerx=self.stage.width/2, centery=15)
        self.stage.screen.blit(fpsText, fpsRect)


# guard to run locally only
if __name__ == '__main__': #(cus this checks if current script is being run directly as the main program)
    initSoundManager()
    game = Asteroids()
    game.playGame()
