
import pygame

SCREEN_SIZE = (1200, 700)

class TextPrint:
   def __init__(self):
      self._startX = 10
      self._startY = 10
      self._indent = 10
      self.reset()
      self._lineHeight = 15
      self._lineWidth = 300
      self._font = pygame.font.Font(None, 20)
      self._joysticks = {}
      
   
   def renderJoy(self, joy, screen):
      # Get the joystick of the given number
      
      if joy not in self._joysticks.keys():
         joystick = pygame.joystick.Joystick(joy)
         
         # Initialize the joystick if it is not yet
         if not joystick.get_init():
            joystick.init()
         
         self._joysticks[joy] = joystick
  
      # Display the joystick's number
      self.renderText(screen, "Joystick {}".format(joy) )
      self.indent()
  
      # Get the name from the OS for the controller/joystick
      name = self._joysticks[joy].get_name()
      self.renderText(screen, "Joystick name: {}".format(name) )
      
      # Usually axis run in pairs, up/down for one, and left/right for
      # the other.
      axes = self._joysticks[joy].get_numaxes()
      self.renderText(screen, "Number of axes: {}".format(axes) )
      self.indent()
      
      for i in range( axes ):
         axis = self._joysticks[joy].get_axis( i )
         self.renderText(screen, "Axis {} value: {:>6.3f}".format(i, axis) )
      self.unindent()
          
      # Display buttons
      buttons = self._joysticks[joy].get_numbuttons()
      self.renderText(screen, "Number of buttons: {}".format(buttons) )
      self.indent()

      for i in range( buttons ):
         button = self._joysticks[joy].get_button( i )
         self.renderText(screen, "Button {:>2} value: {}".format(i,button) )
      self.unindent()
          
      # Hat switch. All or nothing for direction, not like joysseconds.
      # Value comes back in an array.
      hats = self._joysticks[joy].get_numhats()
      self.renderText(screen, "Number of hats: {}".format(hats) )
      self.indent()

      for i in range( hats ):
         hat = self._joysticks[joy].get_hat( i )
         self.renderText(screen, "Hat {} value: {}".format(i, str(hat)) )
      self.unindent()
      
      self.unindent()

   def renderText(self, screen, textString):
      # Render some text at the current location and move down a line
      textBitmap = self._font.render(textString, True, (0,0,0))
      screen.blit(textBitmap, [self._x, self._y])
      self._y += self._lineHeight
       
   def reset(self):
      # Go back to the top left
      self._x = self._startX
      self._y = self._startY
       
   def indent(self):
      # "tab" over
      self._x += self._indent
       
   def unindent(self):
      # undo tab
      self._x -= self._indent
      
   def nextJoy(self):
      # Return to the top and move to the right
      self._x += self._lineWidth
      self._y = self._startY + self._lineHeight
      
      

def main():
   
   # initialize the pygame module
   pygame.init()
   # load and set the logo
   
   pygame.display.set_caption("Joystick Controls")
   
   screen = pygame.display.set_mode(SCREEN_SIZE)
   
   
   textPrint = TextPrint()   
   
   # define a variable to control the main loop
   RUNNING = True
   
   # main loop
   while RUNNING:
      
      # Draw everything
      screen.fill((255,255,255))
      textPrint.reset()
      
      # Get count of joysseconds
      joystick_count = pygame.joystick.get_count()
      
      textPrint.renderText(screen, "Number of joysticks: {}".format(joystick_count) )
      textPrint.indent()
      
      # For each joystick:
      for i in range(joystick_count):
         textPrint.renderJoy(i, screen)
         textPrint.nextJoy()
      
      # Flip the display to the monitor
      pygame.display.flip()
      
      # event handling, gets all event from the eventqueue
      for event in pygame.event.get():
         # only do something if the event is of type QUIT or ESCAPE is pressed
         if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            # change the value to False, to exit the main loop
            RUNNING = False
         
            
      
   pygame.quit()
      
if __name__ == "__main__":
   main()