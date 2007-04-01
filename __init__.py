# Make a shortcut to the Jpeg and Tiff classes, which are exported directly
import jpeg, tiff
Jpeg = jpeg.Jpeg
Tiff = tiff.Tiff

# The __all__ list contains the modules we can handle.
__all__ = ["Jpeg", "Tiff"]
