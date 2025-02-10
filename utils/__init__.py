from .config import Manager
import os

config_manager = Manager()
config_manager.load_vars()