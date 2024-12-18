import configparser
from constants import DEFAULT_BAUD_RATE, GAME_MODES

class ConfigManager:
    def __init__(self, config_file='tictactoe.ini'):
        self.config_file = config_file
        self.config = self.load_config()

    def load_config(self):
        """Load configuration from file or create default if not exists."""
        config = configparser.ConfigParser()
        try:
            config.read(self.config_file)
        except:
            self._create_default_config(config)
        return config

    def _create_default_config(self, config):
        """Create default configuration."""
        config['Serial'] = {'baud_rate': DEFAULT_BAUD_RATE}
        config['Game'] = {'default_mode': GAME_MODES[0]}
        self.save_config()

    def save_config(self):
        """Save current configuration to file."""
        with open(self.config_file, 'w') as f:
            self.config.write(f)

    def get_baud_rate(self):
        """Get configured baud rate."""
        return self.config.get('Serial', 'baud_rate', fallback=DEFAULT_BAUD_RATE)

    def get_default_mode(self):
        """Get configured default game mode."""
        return self.config.get('Game', 'default_mode', fallback=GAME_MODES[0])

    def set_baud_rate(self, baud_rate):
        """Set new baud rate."""
        self.config['Serial']['baud_rate'] = str(baud_rate)

    def set_default_mode(self, mode):
        """Set new default game mode."""
        self.config['Game']['default_mode'] = mode