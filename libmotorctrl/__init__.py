import importlib.metadata
from .drive_manager import DriveManager, DriveTarget
from .drive import DriveState, DriveError, DriveActionError

__version__ = importlib.metadata.version(__package__ or __name__)
