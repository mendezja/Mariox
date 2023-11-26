from enum import Enum

class Actions(Enum):
    JUMP = "jump"
    LEFT = "left"
    RIGHT = "right"
    SHOOT = "shoot"
    SWP_GUN1 = "swp_gun1"
    SWP_GUN2 = "swp_gun2"
    FALL = "fall"
    STOPLEFT = "stopleft"
    STOPRIGHT = "stopright"
    # Add more actions here as needed
    
    # To use, call Actions.JUMP, etc.

    # To use it in a function, use Actions as the type
    # def perform_action(action: Actions):
    #   Your code here
    #   print(f"Performing action: {action.value}")

