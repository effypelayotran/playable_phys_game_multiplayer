#
# 210212 RJG Readme and minor mods
#

import pygame
import sys
import os
from pygame.locals import *
from shooter import *
import gameParameters


class Stage:

    # Set up the PyGame surface
    def __init__(self, caption, dimensions=None):
        pygame.init()

        # If no screen size is provided pick the first available mode
        if dimensions == None:
            dimensions = pygame.display.list_modes()[0]

        # pygame.display.set_mode(dimensions, FULLSCREEN) # This is the original instruction, https://www.pygame.org/docs/ref/display.html#pygame.display.set_mode
        pygame.display.set_mode(dimensions, SHOWN ) # Not Fullscreen
        pygame.mouse.set_visible(False)

        pygame.display.set_caption(caption)
        self.screen = pygame.display.get_surface()
        self.spriteList = []
        self.width = dimensions[0]
        self.height = dimensions[1]
        self.showBoundingBoxes = False
        # self.spaceShipList = [] # Not used


    # Add sprite to list then draw it as a easy way to get the bounding rect
    def addSprite(self, sprite):
        self.spriteList.append(sprite)
        sprite.boundingRect = pygame.draw.aalines(
            self.screen, sprite.color, True, sprite.draw())


    def removeSprite(self, sprite):
        self.spriteList.remove(sprite)


    def drawSprites(self):
        for sprite in self.spriteList:
            sprite.boundingRect = pygame.draw.aalines(
                self.screen, sprite.color, True, sprite.draw())
            if self.showBoundingBoxes == True:
                pygame.draw.rect(self.screen, (255, 255, 255),
                                 sprite.boundingRect, 1)


    def moveSprites(self):
        for sprite in self.spriteList:
            sprite.move()

            if sprite.position.x < 0:
                sprite.position.x = self.width

            if sprite.position.x > self.width:
                sprite.position.x = 0

            if sprite.position.y < 0:
                sprite.position.y = self.height

            if sprite.position.y > self.height:
                sprite.position.y = 0