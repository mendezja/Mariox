from .drawable import Drawable
from .vector2D import Vector2
from ..managers.frameManager import FrameManager
import pygame


class RepeatingSprite(Drawable):

    def __init__(self, dimensions: Vector2, imageName: str, position=Vector2(0, 0), offset=None, parallax=1):
        super().__init__("", position, offset, parallax)
        self._dimensions = dimensions

        self._showBox = False
        self._imageName = imageName

        # Load one tile to get the width and height
        self._tile = FrameManager.getInstance().getFrame(imageName, offset)
        self._tileSize = self._tile.get_size()

        self._image = pygame.Surface(list(self._dimensions))
        self._image.fill((0, 255, 255))
        self._image.set_colorkey(self._image.get_at((0, 0)))

        for x in range(0, self._dimensions[0], self._tileSize[0]):
            for y in range(0, self._dimensions[1], self._tileSize[1]):

                self._image.blit(self._tile, (x, y))

                if self._showBox:
                    pygame.draw.rect(self._image, (0, 255, 0),
                                     pygame.Rect((x, y), self._tileSize), 1)

    def toggleBox(self):
        self._showBox = not self._showBox

        self._image.fill((0, 255, 255))

        for x in range(0, self._dimensions[0], self._tileSize[0]):
            for y in range(0, self._dimensions[1], self._tileSize[1]):

                self._image.blit(self._tile, (x, y))

                if self._showBox:
                    pygame.draw.rect(self._image, (0, 255, 0),
                                     pygame.Rect((x, y), self._tileSize), 1)


class EfficientBackground(RepeatingSprite):
    def __init__(self, screenSize, imageName, position=Vector2(0, 0), offset=None, parallax=1):

        dimensions = screenSize * 2
        self._tile = FrameManager.getInstance().getFrame(imageName, offset)

        if dimensions[0] < self.getSize()[0] * 2:
            dimensions[0] = self.getSize()[0] * 2

        if dimensions[1] < self.getSize()[1] * 2:
            dimensions[1] = self.getSize[1] * 2

        super().__init__(dimensions, imageName, position, offset, parallax)

    def getSize(self):
        return self._tile.get_size()

    def update(self):

        if self._parallax != 0:
            topLeft = Drawable.CAM_OFFSET1 * self._parallax
            imageSize = self.getSize()

            # Adjust location if we've moved
            if self._position.x + imageSize[0] < topLeft.x:
                self._position.x += imageSize[0]

            elif self._position.x > topLeft.x:
                self._position.x -= imageSize[0]

            if self._position.y + imageSize[1] < topLeft.y:
                self._position.y += imageSize[1]

            elif self._position.y > topLeft.y:
                self._position.y -= imageSize[1]

    def setAlpha(self, amount):
        self._image.set_alpha(amount)


# class MovingBackground(EfficientBackground):
#     def __init__(self, screenSize, imageName, velocity, position=Vector2(0, 0), offset=None, parallax=1):
#         super().__init__(screenSize, imageName, position, offset, parallax)

#         self._velocity = velocity

#     def update(self, seconds):
#         self._position = self._position + self._velocity * seconds

#         super().update()


# class Floor(Drawable):
#     def __init__(self, width, yPos):
#         super().__init__("", Vector2(0, yPos))
#         self._image = pygame.Surface((width, 16))
#         self._tile = Drawable("brick.png", (0, 0))._image

#         for x in range(0, width, 16):
#             self._image.blit(self._tile, (x, 0))

