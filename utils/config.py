import os
import configparser


class Manager:
    """
    A configuration management class for handling environment-specific settings.

    This class provides functionality to load, create, and manage configuration variables 
    from an INI file. It allows dynamic configuration of environment variables, with the 
    ability to reset or recreate the configuration as needed.

    Attributes:
        file (str): Path to the configuration file (default is 'config.ini')
        config_vars (dict): A dictionary to store configuration variables after loading

    Key Methods:
        load_vars(): Loads configuration variables from the INI file into environment variables
        reset_config(): Removes the existing configuration file and creates a new template
        __create_config_template(): Creates a default configuration file with predefined variables

    Example:
        >>> config_manager = Manager()
        >>> config_manager.load_vars()
        >>> # Access environment variables
        >>> bucket_name = os.environ.get('BUCKET_NAME')
    """

    def __init__(self, config_path: str = 'config.ini'):

        self.utils_dir = os.path.dirname(__file__)
        self.file = os.path.join(self.utils_dir, config_path)
        self.config_vars = {}

    def load_vars(self):

        if not os.path.isfile(self.file):
            self.__create_config_template()

        config = configparser.ConfigParser()
        config.read(self.file)

        self.__read_config_section(config, 'Settings')
        self.__read_config_section(config, 'Scrapper Settings')

        # Other custom Vars here - if any
        os.environ['HOME_DIR'] = os.path.dirname(self.utils_dir)

    def reset_config(self):

        print("Resetting Configuration")
        os.remove(self.file)
        self.config_vars = {}
        self.__create_config_template()

    def __read_config_section(self, config, section_name):

        for key, value in config[section_name].items():
            value = value.strip("'\"")

            # Set environment variable
            os.environ[key.upper()] = value
            self.config_vars[key.upper()] = value

    def __create_config_template(self):

        config = configparser.ConfigParser()

        config['Settings'] = {
            'rawdata_dir': 'data/raw/',
        }
        config['Scrapper Settings'] = {
            'sitemap': 'https://international.northeastern.edu/ogs',
            'workers': '30',
        }

        with open(self.file, 'w+') as configfile:
            config.write(configfile)

        print(f"Configuration file created")
