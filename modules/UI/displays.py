
from ..gameObjects.drawable import Drawable
from ..gameObjects.vector2D import Vector2
from .items import *
import pygame
from pygame.event import Event


class AbstractMenu(Drawable):
    """Abstract class for basic menus."""

    def __init__(self, background,
                 fontName="default", color=(255, 255, 255)):
        super().__init__(background, (0, 0), parallax=0)

        self._options: dict[str, Text] = {}

        self._color = color
        self._font = fontName

    def addOption(self, key, text, position, center=None):
        self._options[key] = Text(position, text, self._font, self._color)

        if center != None:

            x = position[0]
            y = position[1]

            size = self._options[key].getSize()

            if center in ["horizontal", "both"]:
                x -= size[0] // 2

            if center in ["veritcal", "both"]:
                y -= size[1] // 2

            position = Vector2(x, y)

            self._options[key].setPosition(position)

    def draw(self, surface):
        super().draw(surface, noOffset=True)

        for item in self._options.values():
            item.draw(surface, noOffset=True)

    def update(self, seconds):
        pass


class CursorMenu(AbstractMenu):
    """Menu which uses directional keys/a cursor for selection."""

    def __init__(self, background, cursor="arrow.png",
                 fontName="default", color=(255, 255, 255)):
        super().__init__(background, fontName, color)

        self._cursor = Drawable(cursor, Vector2(0, 0), parallax=0)
        self._current = None

        self._controls = {
            pygame.K_UP: "up",
            pygame.K_DOWN: "down",
            pygame.K_RIGHT: "right",
            pygame.K_LEFT: "left",
            "UP": "up",
            "DOWN": "down"
        }

    def addOption(self, key, text, position, center=None):
        super().addOption(key, text, position, center)

        self._current = key
        self._moveCursor()

    def setCursor(self, key):
        self._current = key
        self._moveCursor()

    def draw(self, surface):
        super().draw(surface)
        self._cursor.draw(surface, noOffset=True)

    def _moveCursor(self):
        self._cursor.setPosition(self._options[self._current].getPosition(
        ) - Vector2(self._cursor.getCollisionRect().width, 0))

    def _findNearestInDirection(self, direction):

        currentPosition = self._options[self._current].getPosition()

        nearest = None

        for key in self._options.keys():
            keyPosition = self._options[key].getPosition()

            if (direction == "up" and keyPosition[1] < currentPosition[1]) or \
               (direction == "down" and keyPosition[1] > currentPosition[1]) or \
               (direction == "left" and keyPosition[0] < currentPosition[0]) or \
               (direction == "right" and keyPosition[0] > currentPosition[0]):

                if nearest == None or (keyPosition - currentPosition).magnitude() < (self._options[nearest].getPosition() - currentPosition).magnitude():
                    nearest = key

        return nearest

    def handleEvent(self, event: Event):
        # Keyboard
        if event.type == pygame.KEYDOWN:
            if event.key in self._controls.keys():
                newCurr = self._findNearestInDirection(
                    self._controls[event.key])

                if newCurr != None:
                    self._current = newCurr
                    self._moveCursor()

            elif event.key == pygame.K_RETURN:
                return self._current

        # Joystick
        elif event.type == pygame.JOYAXISMOTION:
            if event.axis == 1:
                if abs(event.value) < 0.1:
                    return
                newCurr = self._findNearestInDirection(
                    self._controls["DOWN" if event.value > 0 else "UP"])

                if newCurr != None:
                    self._current = newCurr
                    self._moveCursor()
        elif event.type == pygame.JOYBUTTONDOWN:
            if event.button == 8:
                return self._current
