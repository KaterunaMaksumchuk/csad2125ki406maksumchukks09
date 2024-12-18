# Game modes
GAME_MODES = ['Man vs Man', 'Man vs AI', 'AI vs AI']
MODE_MAP = {'Man vs Man': 1, 'Man vs AI': 2, 'AI vs AI': 3}

# Serial settings
DEFAULT_BAUD_RATES = ['9600', '19200', '38400', '57600', '115200']
DEFAULT_BAUD_RATE = '9600'

# Style sheets
BUTTON_STYLE = """
    QPushButton {
        background-color: #f9f9f9;
        border: 2px solid #ccc;
        border-radius: 5px;
    }
    QPushButton:hover {
        background-color: #e0e0e0;
    }
"""

CONNECT_BUTTON_STYLE = """
    QPushButton {
        background-color: #4CAF50;
        color: white;
        border-radius: 5px;
    }
    QPushButton:hover {
        background-color: #388E3C;
    }
"""

DISCONNECT_BUTTON_STYLE = """
    QPushButton {
        background-color: #ff4444;
        color: white;
        border-radius: 5px;
    }
"""

RESET_BUTTON_STYLE = """
    QPushButton {
        padding: 10px;
        font-weight: bold;
        background-color: #2196F3;
        color: white;
        border-radius: 5px;
    }
    QPushButton:hover {
        background-color: #1976D2;
    }
"""

# Board markers
MARKER_X = 'X'
MARKER_O = 'O'
MARKER_EMPTY = ''

# Status messages
STATUS_CONNECTED = "Connected"
STATUS_DISCONNECTED = "Disconnected"
STATUS_NOT_CONNECTED = "Not Connected"