import uuid
import os

from .tokenseeder import TokenSeeder
from .download_handler import DownloadHandler

def initialize(config, logger, authenticator):
    tokenseeder = TokenSeeder(config, logger, authenticator)
    return tokenseeder