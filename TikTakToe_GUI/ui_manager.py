from PySide6.QtWidgets import QMainWindow, QPushButton, QMessageBox
from PySide6.QtGui import QFont
from PySide6.QtCore import QTimer
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile
from constants import (GAME_MODES, DEFAULT_BAUD_RATES, BUTTON_STYLE, 
                     CONNECT_BUTTON_STYLE, DISCONNECT_BUTTON_STYLE,
                     STATUS_CONNECTED, STATUS_DISCONNECTED, STATUS_NOT_CONNECTED)

class UIManager(QMainWindow):
    def __init__(self, config_manager, serial_manager, game_process):
        super().__init__()
        self.config_manager = config_manager
        self.serial_manager = serial_manager
        self.game_process = game_process
        self.board_buttons = []
        
        self.load_ui()
        self.init_ui_components()
        self.init_timers()
        self.connect_signals()

    def load_ui(self):
        """Load UI from .ui file."""
        ui_file = QFile("ui/main_window.ui")
        ui_file.open(QFile.ReadOnly)
        loader = QUiLoader()
        self.ui = loader.load(ui_file)
        ui_file.close()
        
        # Set up the main window
        self.setCentralWidget(self.ui)
        self.setWindowTitle("Tic Tac Toe")

    def init_ui_components(self):
        """Initialize UI components."""
        # Set up combo boxes
        self.ui.baud_combo.addItems(DEFAULT_BAUD_RATES)
        self.ui.baud_combo.setCurrentText(self.config_manager.get_baud_rate())
        self.ui.mode_combo.addItems(GAME_MODES)
        self.ui.mode_combo.setCurrentText(self.config_manager.get_default_mode())
        
        # Initialize game board buttons
        for i in range(9):
            btn = QPushButton()
            btn.setFont(QFont('Arial', 24, QFont.Bold))
            btn.setFixedSize(100, 100)
            btn.setStyleSheet(BUTTON_STYLE)
            btn.clicked.connect(lambda checked, pos=i: self.make_move(pos))
            self.board_buttons.append(btn)
            self.ui.board_layout.addWidget(btn, i // 3, i % 3)

        # Set up connection button style
        self.ui.connect_btn.setStyleSheet(CONNECT_BUTTON_STYLE)
        
        # Refresh available ports
        self.refresh_ports()

    def init_timers(self):
        """Initialize timers."""
        # Timer for AI moves
        self.ai_timer = QTimer(self)
        self.ai_timer.timeout.connect(self.check_ai_moves)

        # Timer for connection monitoring
        self.connection_timer = QTimer(self)
        self.connection_timer.timeout.connect(self.check_connection)
        self.connection_timer.start(1000)

    def connect_signals(self):
        """Connect UI signals to slots."""
        self.ui.refresh_btn.clicked.connect(self.refresh_ports)
        self.ui.connect_btn.clicked.connect(self.toggle_connection)
        self.ui.mode_combo.currentTextChanged.connect(self.change_mode)
        self.ui.reset_btn.clicked.connect(self.reset_game)

    def refresh_ports(self):
        """Refresh available serial ports."""
        current_port = self.ui.port_combo.currentText()
        self.ui.port_combo.clear()
        ports = self.serial_manager.get_available_ports()
        self.ui.port_combo.addItems(ports)
        if current_port in ports:
            self.ui.port_combo.setCurrentText(current_port)
        elif ports:
            self.ui.port_combo.setCurrentText(ports[0])

    def toggle_connection(self):
        """Toggle serial connection."""
        if not self.serial_manager.is_connected():
            try:
                port = self.ui.port_combo.currentText()
                if not port:
                    raise ValueError("No port selected")

                baud = int(self.ui.baud_combo.currentText())
                self.serial_manager.connect(port, baud)
                
                self.ui.connect_btn.setText("Disconnect")
                self.ui.connect_btn.setStyleSheet(DISCONNECT_BUTTON_STYLE)
                self.ui.port_combo.setEnabled(False)
                self.ui.baud_combo.setEnabled(False)
                self.ui.status_label.setText(STATUS_CONNECTED)
                self.ui.status_label.setStyleSheet("color: green; font-weight: bold;")
                
                self.reset_game()
                
                if self.ui.mode_combo.currentText() == 'AI vs AI':
                    self.ai_timer.start(100)

            except Exception as e:
                QMessageBox.critical(self, "Connection Error",
                                   f"Failed to connect: {str(e)}\n"
                                   f"Please check if the device is connected and the port is correct.")
        else:
            self.serial_manager.disconnect()
            self.handle_disconnection()

    def handle_disconnection(self):
        """Handle disconnection event."""
        self.ui.connect_btn.setText("Connect")
        self.ui.connect_btn.setStyleSheet(CONNECT_BUTTON_STYLE)
        self.ui.port_combo.setEnabled(True)
        self.ui.baud_combo.setEnabled(True)
        self.ui.status_label.setText(STATUS_DISCONNECTED)
        self.ui.status_label.setStyleSheet("color: red; font-weight: bold;")
        self.ai_timer.stop()
        self.game_process.reset_game()

    def check_connection(self):
        """Check if connection is still active."""
        if self.serial_manager.is_connected():
            self.ui.status_label.setText(STATUS_CONNECTED)
            self.ui.status_label.setStyleSheet("color: green; font-weight: bold;")
        else:
            self.handle_disconnection()

    def make_move(self, position):
        """Make a move in the game."""
        if not self.serial_manager.is_connected():
            QMessageBox.warning(self, "Warning",
                              "Not connected to Arduino.\nPlease connect first.")
            return

        try:
            result = self.game_process.make_move(position)
            if result:
                self.update_board(result)
        except ConnectionError:
            self.handle_disconnection()

    def update_board(self, result):
        """Update board UI based on game result."""
        if result.get('board_state'):
            for i, marker in enumerate(result['board_state']):
                self.board_buttons[i].setText(marker)
                if marker == 'X':
                    self.board_buttons[i].setStyleSheet("color: #c23434;")
                elif marker == 'O':
                    self.board_buttons[i].setStyleSheet("color: #3dcbcb;")

        if result.get('game_over'):
            if result.get('winner'):
                QMessageBox.information(self, "Game Over",
                                      f"Player {result['winner']} wins!")
            elif result.get('draw'):
                QMessageBox.information(self, "Game Over",
                                      "It's a draw!")
            
            if self.ui.mode_combo.currentText() == 'AI vs AI':
                self.ai_timer.stop()

        if result.get('error'):
            QMessageBox.warning(self, "Game Error", result['error'])

    def check_ai_moves(self):
        """Check and process AI moves."""
        if self.serial_manager.is_connected() and self.ui.mode_combo.currentText() == 'AI vs AI':
            try:
                result = self.game_process.process_response()
                if result:
                    self.update_board(result)
            except ConnectionError:
                self.handle_disconnection()

    def change_mode(self, mode):
        """Change game mode."""
        try:
            if self.serial_manager.is_connected():
                if self.game_process.set_mode(mode):
                    self.reset_game()
                    if mode == 'AI vs AI':
                        self.ai_timer.start(100)
                    else:
                        self.ai_timer.stop()
        except ConnectionError:
            self.handle_disconnection()

    def reset_game(self):
        """Reset game state and board."""
        for btn in self.board_buttons:
            btn.setText("")
            btn.setStyleSheet(BUTTON_STYLE)
        self.game_process.reset_game()

    def closeEvent(self, event):
        """Handle window close event."""
        try:
            self.serial_manager.disconnect()
            
            # Save settings
            self.config_manager.set_baud_rate(self.ui.baud_combo.currentText())
            self.config_manager.set_default_mode(self.ui.mode_combo.currentText())
            self.config_manager.save_config()
            
            event.accept()
        except Exception as e:
            print(f"Error during closing: {e}")
            event.accept()