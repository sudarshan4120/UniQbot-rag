from .config import Manager
import os

def import_settings():
    print("Setting Configurations")
    config_manager = Manager()
    config_manager.load_vars()

if __name__ == "__main__":
    import_settings()