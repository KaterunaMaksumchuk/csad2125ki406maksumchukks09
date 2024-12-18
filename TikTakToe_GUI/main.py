import sys
from PySide6.QtWidgets import QApplication
from config_manager import ConfigManager
from serial_manager import SerialManager
from game_process import GameProcess
from ui_manager import UIManager

def main():
    try:
        # Create application instance
        app = QApplication(sys.argv)
        app.setStyle('Fusion')

        # Initialize managers
        config_manager = ConfigManager()
        serial_manager = SerialManager()
        game_process = GameProcess(serial_manager)
        
        # Create and show main window
        window = UIManager(config_manager, serial_manager, game_process)
        window.show()

        # Start application event loop
        sys.exit(app.exec())

    except KeyboardInterrupt:
        print("\nProgram finished correctly")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()