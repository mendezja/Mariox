"""
A Singleton Frame Manager class
Author: Liz Matthews, 9/20/2019

Provides on-demand loading of images for a pygame program. Will load entire sprite sheets if given an offset.

"""


from pygame import image, Surface, Rect, SRCALPHA
from os.path import join


class FrameManager(object):
    """A singleton factory class to create and store frames on demand."""

    # The singleton instance variable
    _INSTANCE = None

    @classmethod
    def getInstance(cls):
        """Used to obtain the singleton instance"""
        if cls._INSTANCE == None:
            cls._INSTANCE = cls._FM()

        return cls._INSTANCE

    # Do not directly instantiate this class!
    class _FM(object):
        """An internal FrameManager class to contain the actual code. Is a private class."""

        # Folder in which images are stored
        _IMAGE_FOLDER = "images"

        # Static information about the frame sizes of particular image sheets.
        _FRAME_SIZES = {
            "mario.png": (16,17),
            "brick.png": (16,16),
            "background.png": (2624,240),
            "enemies.png": (20,15)              #create var here for enemies/mario
        }

        # A default frame size
        _DEFAULT_FRAME = (32, 32)

        # A list of images that require to be loaded with transparency
        _TRANSPARENCY = []

        # A list of images that require to be loaded with a color key
        _COLOR_KEY = [ "enemies.png", "mario.png"]
        
        #@classmethod
        #def setFrameSize(cls, spriteSheetName: str, newSize: tuple):
        #    cls._FRAME_SIZES[spriteSheetName] = newSize
        
        
        def __init__(self):
            # Stores the surfaces indexed based on file name
            # The values in _surfaces can be a single Surface
            #  or a two dimentional grid of surfaces if it is an image sheet
            self._surfaces = {}

        def __getitem__(self, key) -> Surface:
            return self._surfaces[key]

        def __setitem__(self, key, item):
            self._surfaces[key] = item        

        def getFrame(self, fileName, offset=None) -> Surface:
            # If this frame has not already been loaded, load the image from memory
            if fileName not in self._surfaces.keys():
                self._loadImage(fileName, offset != None)

            # If this is an image sheet, return the correctly offset sub surface
            if offset != None:
                return self[fileName][offset[1]][offset[0]]

            # Otherwise, return the sheet created
            return self[fileName]

        def _loadImage(self, fileName, sheet=False) -> None:
            # Load the full image
            fullImage = image.load(
                join(FrameManager._FM._IMAGE_FOLDER, fileName))

            # Look up some information about the image to be loaded
            transparent = fileName in FrameManager._FM._TRANSPARENCY
            colorKey = fileName in FrameManager._FM._COLOR_KEY

            # Detect if a transparency is needed
            if transparent:
                fullImage = fullImage.convert_alpha()
            else:
                fullImage = fullImage.convert()

            # If the image to be loaded is an image sheet, split it up based on the frame size
            if sheet:

                self[fileName] = []

                # Try to get the sprite size, use the default size if it is not stored
                spriteSize = FrameManager._FM._FRAME_SIZES.get(
                    fileName, FrameManager._FM._DEFAULT_FRAME)

                # See how big the sprite sheet is
                sheetDimensions = fullImage.get_size()

                # Iterate over the entire sheet, increment by the sprite size
                for y in range(0, sheetDimensions[1], spriteSize[1]):
                    self[fileName].append([])
                    for x in range(0, sheetDimensions[0], spriteSize[0]):

                        # If we need transparency
                        if transparent:
                            frame = Surface(spriteSize, SRCALPHA, 32)
                        else:
                            frame = Surface(spriteSize)

                        frame.blit(fullImage, (0, 0), Rect((x, y), spriteSize))

                        # If we need to set the color key
                        if colorKey:
                            frame.set_colorkey(frame.get_at((0, 0)))

                        # Add the frame to the end of the current row
                        self[fileName][-1].append(frame)
            else:
                # Not a sprite sheet, full image is what we wish to store
                self[fileName] = fullImage

                # If we need to set the color key
                if colorKey:
                    self[fileName].set_colorkey(self[fileName].get_at((0, 0)))
