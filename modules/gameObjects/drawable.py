from typing import Tuple
import pygame
from pygame import Surface
from pygame import Rect

from .vector2D import Vector2
from ..managers.frameManager import FrameManager


class BasicState(object):
    def __init__(self, facing="none"):
        self._facing = facing

    def getFacing(self):
        return self._facing

    def _setFacing(self, direction):
        self._facing = direction


class Drawable(object):
    CAM_OFFSET1 = Vector2(0, 0)
    CAM_OFFSET2 = Vector2(0, 0)

    _IMAGE_RECTS = {
        "mario.png": Rect(2, 0, 13, 16),
        "luigi.png": Rect(2, 0, 13, 16),
        "enemies.png": Rect(5, 0, 16, 15)
    }

    @classmethod
    def updateOffset(cls, tracked, screenSize, worldSize, whichPlayer=None):
        position = tracked.getPosition()
        size = tracked.getSize()
        offset = Vector2(min(max(0, position[0] + (size[0] // 2) - (screenSize[0] // 2)),
                             worldSize[0] - screenSize[0]),
                         min(max(0, position[1] + (size[1] // 2) - ((screenSize[1]) // 2)),
                             worldSize[1] - screenSize[1] // 2) + 30)
        if whichPlayer == 0:  # Bottom screen
            cls.CAM_OFFSET2 = offset
        elif whichPlayer == 1:  # Top screen
            cls.CAM_OFFSET1 = offset
        else:  # single player
            cls.CAM_OFFSET1 = Vector2(min(max(0, position[0] + (size[0] // 2) - (screenSize[0] // 2)),
                                          worldSize[0] - screenSize[0]),
                                      min(max(0, position[1] + (size[1] // 2) - ((screenSize[1]) // 2)),
                                          worldSize[1] - screenSize[1]))

    def __init__(self, imageName: str, position: tuple, offset=None, parallax=1):
        self._imageName = imageName

        # Let frame manager handle loading the image
        self._image = FrameManager.getInstance().getFrame(self._imageName, offset)

        self._position = Vector2(*position)
        self._parallax = parallax
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
        # print(self._image.get_rect())
        if self._imageName in self._IMAGE_RECTS:
            newRect = self._position + self._IMAGE_RECTS[self._imageName]
        else:
            newRect = self._position + self._image.get_rect()
        return newRect

    def draw(self, surface: Surface, whichPlayer=None, noOffset=False):
        blitImage = self._image
        offset = None

        if whichPlayer != None:  # Two players
            offset = (Drawable.CAM_OFFSET1 if whichPlayer ==
                      1 else Drawable.CAM_OFFSET2)
        else:  # 1 player
            offset = Drawable.CAM_OFFSET1

        if self._state.getFacing() == "left":
            blitImage = pygame.transform.flip(self._image, True, False)

        x = int(self._position.x) if noOffset else int(
            self._position.x - offset.x)
        y = int(self._position.y) if noOffset else int(
            self._position.y - offset.y)

        surface.blit(blitImage, (x, y))
