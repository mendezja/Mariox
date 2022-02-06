from typing import Tuple
import pygame
from pygame import Surface
from .vector2D import Vector2
from .frameManager import FrameManager


class BasicState(object):
    def __init__(self, facing="none"):
        self._facing = facing

    def getFacing(self):
        return self._facing

    def _setFacing(self, direction):
        self._facing = direction


class Drawable(object):

    def __init__(self, imageName, position: tuple, offset=None):
        self._imageName = imageName

        # Let frame manager handle loading the image
        self._image = FrameManager.getInstance().getFrame(self._imageName, offset)

        self._position = Vector2(*position)
        self._state = BasicState()

    def getPosition(self) -> Vector2:
        return self._position

    def setPosition(self, newPosition):
        self._position = newPosition

    def getSize(self) -> Tuple[int, int]:
        return self._image.get_size()

    def setImage(self, surface):
        self._image = surface

    def getCollisionRect(self):
        newRect = self._position + self._image.get_rect()
        return newRect

    def draw(self, surface: Surface):
        blitImage = self._image

        if self._state.getFacing() == "left":
            blitImage = pygame.transform.flip(self._image, True, False)

        surface.blit(blitImage, (self._position[0], self._position[1]))
