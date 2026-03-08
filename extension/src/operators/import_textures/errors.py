from enum import Enum, auto
from ...constants import MIN_VERSION

class Errors(Enum):
    MC_NOT_FOUND = auto()
    NO_VERSION_INSTALLED = auto()
    MIN_VERSION_EXCEEDED = auto()
    VERSION_FILE_NOT_FOUND = auto()
    NOT_ALL_TEXTURES = auto()
    ENCHANTED_BOOK = auto()


    def error_text(self):
        descriptions = {
            Errors.MC_NOT_FOUND: "Minecraft could not be found",
            Errors.NO_VERSION_INSTALLED: "No Minecraft version installed",
            Errors.MIN_VERSION_EXCEEDED: f'Minimum version requirement {MIN_VERSION} not met',
            Errors.VERSION_FILE_NOT_FOUND: "MC Version.jar file not found",
            Errors.NOT_ALL_TEXTURES: "Not all needed textures found",
            Errors.ENCHANTED_BOOK: "Could not create enchanted book icon"  
        }
        return descriptions.get(self, "Unknown error.")