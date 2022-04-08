import pygame, os
from ..managers.frameManager import FrameManager
from .drawable import Drawable 
from ..gameObjects.drawable import Drawable 


class BasicItemManager(Drawable):
   """Basic ItemManager class for countable item display."""
   def __init__(self, background="", position=(0,0), parallax=0):
      super().__init__(background, position, parallax=parallax)
      self._items = {}
   
   def addItem(self, key, item):
      self._items[key] = item
   
   def changeItem(self, key, value):
      self._items[key].change(value)
   
   def increaseItem(self, key, value=1):
      self._items[key].increase(value)
   
   def decreaseItem(self, key, value=1):
      self._items[key].decrease(value)
      
   def getItemValue(self, key):
      return self._items[key].getValue()
   
   def draw(self, surface):
      if self._imageName != "":
         super().draw(surface)
      for item in self._items.values():
         item.draw(surface)
   
   def update(self, seconds):
      for item in self._items.values():
         item.update(seconds)




class AbstractUIEntry(Drawable):
   """ Basic UI Entry Class
   Sets parallax to zero and contains information about fonts"""
   
   if not pygame.font.get_init():
      pygame.font.init()
   
   _FONT_FOLDER = os.path.join("resources", "fonts")   
   _DEFAULT_FONT = "PressStart2P.ttf"
   _DEFAULT_SIZE = 8 #16
   
   FONTS = {
      "default" : pygame.font.Font(os.path.join(_FONT_FOLDER, _DEFAULT_FONT), _DEFAULT_SIZE),
      "default8" : pygame.font.Font(os.path.join(_FONT_FOLDER, _DEFAULT_FONT), 8)
   }
   
   
   def __init__(self, position):
      super().__init__("", position, parallax=0)

      
class Text(AbstractUIEntry):
    """A plain text UI entry."""

    def __init__(self, position, text, font="default", color=(255, 255, 255)):
        super().__init__(position)
        self._color = color

        self._image = AbstractUIEntry.FONTS[font].render(
            text, False, self._color)      
   
class RectBarItem(AbstractUIEntry):
   """Abstract class for countable UI items."""
   def __init__(self, areaRect, initialValue, maxValue=10,
                color=(255,0,0), outline=(100,100,100), outlineWidth=2, backgroundColor=None, position = (10,10)):
      super().__init__(position)
      self._value = initialValue      
      self._maxValue = maxValue
      self._minValue = 0
      self._areaRect = areaRect
      self._color = color
      self._outline = outline
      self._outlineWidth=outlineWidth
      self._backgroundColor = backgroundColor
      
      self._render()

   def _render(self):
      self._valueRect = pygame.Rect(self._areaRect.left, self._areaRect.top, int(self._areaRect.width * (self._value / self._maxValue)), self._areaRect.height)

   def draw(self, surface):
      drawPosition = self._position - Drawable.CAM_OFFSET1 * self._parallax
      if self._backgroundColor:
         pygame.draw.rect(surface, self._backgroundColor,
                          drawPosition + self._areaRect)
      pygame.draw.rect(surface, self._color, drawPosition + self._valueRect)
      pygame.draw.rect(surface, self._outline, drawPosition + self._areaRect, self._outlineWidth)

   def getValue(self):
      return self._value   
   
   def change(self, value):
      self._value = max(self._minValue, min(self._maxValue, value))      
      self._render()
   
   def increase(self, value = 1):
      self.change(self._value + value)
   
   
   def decrease(self, value = 1):
      self.change(self._value - value)
   
   def setMax(self, value):
      self._maxValue = value
      self._render()
   
   def setMin(self, value):
      self._minValue = value
      self._render()
   
   def update(self, seconds):
      pass

