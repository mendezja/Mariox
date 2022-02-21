from ..gameObjects.vector2D import Vector2


SCREEN_SIZE = Vector2(240, 240)

SCALE = 3
UPSCALED_SCREEN_SIZE = SCREEN_SIZE * SCALE


def adjustMousePos(mousePos):
    return Vector2(*mousePos) // SCALE
