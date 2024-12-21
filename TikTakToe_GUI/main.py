import sys
import configparser
import serial
import serial.tools.list_ports
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout,
                             QHBoxLayout, QWidget, QComboBox, QLabel, QMessageBox,
                             QGridLayout)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QPalette, QColor


class TicTacToeGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.init_game_state()
        self.init_timers()
        self.apply_dark_palette()
        
        # Set global style for QMessageBox
        self.setStyleSheet("""
            QMessageBox {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QMessageBox QLabel {
                color: #ffffff;
            }
            QMessageBox QPushButton {
                background-color: #3b3b3b;
                border: 1px solid #555;
                border-radius: 3px;
                color: #ffffff;
                min-width: 80px;
                padding: 5px;
            }
            QMessageBox QPushButton:hover {
                background-color: #454545;
                border-color: #666;
            }
            QMessageBox QPushButton:pressed {
                background-color: #2a2a2a;
            }
        """)


    def apply_dark_palette(self):
        # Create and apply dark palette
        dark_palette = QPalette()
        
        # Set color roles
        dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.WindowText, QColor(255, 255, 255))
        dark_palette.setColor(QPalette.Base, QColor(35, 35, 35))
        dark_palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ToolTipBase, QColor(255, 255, 255))
        dark_palette.setColor(QPalette.ToolTipText, QColor(255, 255, 255))
        dark_palette.setColor(QPalette.Text, QColor(255, 255, 255))
        dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ButtonText, QColor(255, 255, 255))
        dark_palette.setColor(QPalette.BrightText, QColor(255, 0, 0))
        dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
        
        self.setPalette(dark_palette)

    def init_ui(self):
        self.setWindowTitle("Tic Tac Toe Game")
        self.setMinimumSize(500, 600)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2b2b2b;
            }
            QPushButton {
                background-color: #3b3b3b;
                border: 2px solid #555;
                border-radius: 5px;
                color: #ffffff;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #454545;
                border-color: #666;
            }
            QPushButton:pressed {
                background-color: #2a2a2a;
            }
            QLabel {
                color: #ffffff;
                font-size: 12px;
            }
            QComboBox {
                background-color: #3b3b3b;
                border: 1px solid #555;
                border-radius: 3px;
                color: #ffffff;
                padding: 5px;
            }
            QComboBox:drop-down {
                border: none;
                background-color: #4b4b4b;
            }
            QComboBox::down-arrow {
                border: none;
                color: #ffffff;
            }
            QComboBox QAbstractItemView {
                background-color: #3b3b3b;
                color: #ffffff;
                selection-background-color: #4b4b4b;
            }
        """)

        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)

        # Add connection controls
        layout.addLayout(self.create_connection_controls())

        # Add status label
        self.status_label = QLabel("Not Connected")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("font-weight: bold; color: #ff4444;")
        layout.addWidget(self.status_label)

        # Add game mode controls
        mode_layout = self.create_game_mode_controls()
        layout.addLayout(mode_layout)

        # Add game board
        layout.addLayout(self.create_game_board())

        # Add reset button
        self.reset_btn = QPushButton("Reset Game")
        self.reset_btn.setStyleSheet("""
            QPushButton {
                padding: 10px;
                font-weight: bold;
                background-color: #2d5a27;
                color: white;
            }
            QPushButton:hover {
                background-color: #366c2f;
            }
        """)
        self.reset_btn.clicked.connect(self.reset_game)
        layout.addWidget(self.reset_btn)

        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)

        # Add connection controls
        layout.addLayout(self.create_connection_controls())

        # Add status label
        self.status_label = QLabel("Not Connected")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(self.status_label)

        # Add game mode controls
        mode_layout = self.create_game_mode_controls()
        layout.addLayout(mode_layout)

        # Add game board
        layout.addLayout(self.create_game_board())

        # Add reset button
        self.reset_btn = QPushButton("Reset Game")
        self.reset_btn.setStyleSheet("""
            QPushButton {
                padding: 10px;
                font-weight: bold;
                background-color: #4CAF50;
                color: white;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.reset_btn.clicked.connect(self.reset_game)
        layout.addWidget(self.reset_btn)

    def create_connection_controls(self):
        conn_layout = QHBoxLayout()
        conn_layout.setSpacing(10)

        # Port selection
        self.port_combo = QComboBox()
        self.refresh_ports()
        conn_layout.addWidget(QLabel("Port:"))
        conn_layout.addWidget(self.port_combo)

        # Refresh button
        refresh_btn = QPushButton("🔄")
        refresh_btn.setToolTip("Refresh Ports")
        refresh_btn.clicked.connect(self.refresh_ports)
        conn_layout.addWidget(refresh_btn)

        # Baud rate selection
        self.baud_combo = QComboBox()
        self.baud_combo.addItems(['9600', '19200', '38400', '57600', '115200'])
        self.config = self.load_config()
        self.baud_combo.setCurrentText(self.config.get('Serial', 'baud_rate', fallback='9600'))
        conn_layout.addWidget(QLabel("Baud:"))
        conn_layout.addWidget(self.baud_combo)

        # Connect button
        self.connect_btn = QPushButton("Connect")
        self.connect_btn.clicked.connect(self.toggle_connection)
        conn_layout.addWidget(self.connect_btn)

        return conn_layout

    def create_game_mode_controls(self):
        mode_layout = QHBoxLayout()
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(['Man vs Man', 'Man vs AI', 'AI vs AI'])
        self.mode_combo.setCurrentText(self.config.get('Game', 'default_mode', fallback='Man vs Man'))
        self.mode_combo.currentIndexChanged.connect(self.change_mode)
        mode_layout.addWidget(QLabel("Game Mode:"))
        mode_layout.addWidget(self.mode_combo)
        return mode_layout

    def create_game_board(self):
        board_layout = QGridLayout()
        board_layout.setSpacing(5)
        self.board_buttons = []

        for i in range(9):
            btn = QPushButton()
            btn.setFont(QFont('Arial', 32, QFont.Bold))
            btn.setFixedSize(100, 100)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #2b2b2b;
                    border: 2px solid #555;
                }
                QPushButton:hover {
                    background-color: #353535;
                    border-color: #666;
                }
            """)
            btn.clicked.connect(lambda checked, pos=i: self.make_move(pos))
            self.board_buttons.append(btn)
            board_layout.addWidget(btn, i // 3, i % 3)

        return board_layout

    def init_game_state(self):
        self.serial_conn = None
        self.game_active = True

    def init_timers(self):
        # Timer for AI moves
        self.ai_timer = QTimer()
        self.ai_timer.timeout.connect(self.check_ai_moves)

        # Timer for connection monitoring
        self.connection_timer = QTimer()
        self.connection_timer.timeout.connect(self.check_connection)
        self.connection_timer.start(1000)

    def load_config(self):
        config = configparser.ConfigParser()
        try:
            config.read('tictactoe.ini')
        except:
            config['Serial'] = {'baud_rate': '9600'}
            config['Game'] = {'default_mode': 'Man vs Man'}
            with open('tictactoe.ini', 'w') as f:
                config.write(f)
        return config

    def refresh_ports(self):
        current_port = self.port_combo.currentText()
        self.port_combo.clear()
        ports = [port.device for port in serial.tools.list_ports.comports()]
        self.port_combo.addItems(ports)
        if current_port in ports:
            self.port_combo.setCurrentText(current_port)
        elif ports:
            self.port_combo.setCurrentText(ports[0])

    def check_connection(self):
        try:
            if self.serial_conn:
                try:
                    self.serial_conn.write(b"\n")
                    self.status_label.setText("Connected")
                    self.status_label.setStyleSheet("color: green; font-weight: bold;")
                except:
                    self.handle_disconnection()
        except KeyboardInterrupt:
            self.closeEvent(None)  # Викликаємо метод закриття вікна
            QApplication.quit()  # Закриваємо додаток

    def handle_disconnection(self):
        self.serial_conn = None
        self.connect_btn.setText("Connect")
        self.connect_btn.setStyleSheet("")
        self.port_combo.setEnabled(True)
        self.baud_combo.setEnabled(True)
        self.status_label.setText("Disconnected")
        self.status_label.setStyleSheet("color: red; font-weight: bold;")
        self.ai_timer.stop()
        self.game_active = True

    def toggle_connection(self):
        if self.serial_conn is None:
            try:
                port = self.port_combo.currentText()
                if not port:
                    raise ValueError("No port selected")

                baud = int(self.baud_combo.currentText())
                self.serial_conn = serial.Serial(port, baud, timeout=1)
                self.connect_btn.setText("Disconnect")
                self.connect_btn.setStyleSheet("background-color: #ff4444; color: white;")
                self.port_combo.setEnabled(False)
                self.baud_combo.setEnabled(False)
                self.status_label.setText("Connected")
                self.status_label.setStyleSheet("color: green; font-weight: bold;")
                self.reset_game()

                if self.mode_combo.currentText() == 'AI vs AI':
                    self.ai_timer.start(100)

            except Exception as e:
                QMessageBox.critical(self, "Connection Error",
                                     f"Failed to connect: {str(e)}\n"
                                     f"Please check if the device is connected and the port is correct.")
                self.serial_conn = None
        else:
            self.serial_conn.close()
            self.handle_disconnection()

    def change_mode(self):
        if self.serial_conn:
            mode_map = {'Man vs Man': 1, 'Man vs AI': 2, 'AI vs AI': 3}
            mode = mode_map[self.mode_combo.currentText()]
            try:
                self.serial_conn.write(f"MODE{mode}\n".encode())
                response = self.serial_conn.readline().decode().strip()
                if response == "OK:MODE_SET":
                    self.reset_game()
                    self.game_active = True
                    if mode == 3:
                        self.ai_timer.start(100)
                    else:
                        self.ai_timer.stop()
            except:
                self.handle_disconnection()

    def make_move(self, position):
        if not self.serial_conn:
            QMessageBox.warning(self, "Warning",
                                "Not connected to Arduino.\nPlease connect first.")
            return

        if not self.game_active:
            return

        if self.mode_combo.currentText() == 'AI vs AI':
            return

        try:
            self.serial_conn.write(f"MOVE{position}\n".encode())
            self.process_response()
        except:
            self.handle_disconnection()


    def process_response(self):
        try:
            response = self.serial_conn.readline().decode().strip()
            if response.startswith("BOARD:"):
                parts = response.split(":")
                board_state = parts[1]

                # Update board buttons with dark theme colors
                for i, state in enumerate(board_state):
                    button = self.board_buttons[i]
                    if state == "0":
                        button.setText("")
                        button.setStyleSheet("""
                            QPushButton {
                                background-color: #2b2b2b;
                                border: 2px solid #555;
                            }
                            QPushButton:hover {
                                background-color: #353535;
                                border-color: #666;
                            }
                        """)
                    elif state == "1":
                        button.setText("X")
                        button.setStyleSheet("""
                            QPushButton {
                                background-color: #2b2b2b;
                                border: 2px solid #555;
                                color: #00ffff;
                            }
                            QPushButton:hover {
                                background-color: #353535;
                                border-color: #666;
                            }
                        """)
                    else:
                        button.setText("O")
                        button.setStyleSheet("""
                            QPushButton {
                                background-color: #2b2b2b;
                                border: 2px solid #555;
                                color: #ff9500;
                            }
                            QPushButton:hover {
                                background-color: #353535;
                                border-color: #666;
                            }
                        """)

                # Handle game end conditions with custom styled message boxes
                if "WIN" in response:
                    winner = "X" if parts[3] == "1" else "O"
                    msg = QMessageBox(self)
                    msg.setWindowTitle("Game Over")
                    msg.setText(f"Player {winner} wins!")
                    msg.setIcon(QMessageBox.Information)
                    
                    # Set custom icon color (if winner is X - cyan, if O - orange)
                    winner_color = "#00ffff" if winner == "X" else "#ff9500"
                    msg.setStyleSheet(msg.styleSheet() + f"""
                        QMessageBox QLabel {{
                            color: {winner_color};
                            font-weight: bold;
                            font-size: 14px;
                        }}
                    """)
                    msg.exec_()
                    
                    self.game_active = False
                    if self.mode_combo.currentText() == 'AI vs AI':
                        self.ai_timer.stop()
                elif "DRAW" in response:
                    msg = QMessageBox(self)
                    msg.setWindowTitle("Game Over")
                    msg.setText("It's a draw!")
                    msg.setIcon(QMessageBox.Information)
                    msg.setStyleSheet(msg.styleSheet() + """
                        QMessageBox QLabel {
                            color: #ffffff;
                            font-weight: bold;
                            font-size: 14px;
                        }
                    """)
                    msg.exec_()
                    
                    self.game_active = False
                    if self.mode_combo.currentText() == 'AI vs AI':
                        self.ai_timer.stop()

            elif response.startswith("ERR:"):
                msg = QMessageBox(self)
                msg.setWindowTitle("Game Error")
                msg.setText(response[4:])
                msg.setIcon(QMessageBox.Warning)
                msg.setStyleSheet(msg.styleSheet() + """
                    QMessageBox QLabel {
                        color: #ff4444;
                        font-weight: bold;
                    }
                """)
                msg.exec_()
        except:
            self.handle_disconnection()

    
    def check_ai_moves(self):
        if self.serial_conn and self.mode_combo.currentText() == 'AI vs AI' and self.game_active:
            if self.serial_conn.in_waiting:
                self.process_response()

    def reset_game(self):
        if self.serial_conn:
            try:
                self.serial_conn.write(b"RESET\n")
                response = self.serial_conn.readline().decode().strip()
                if response == "OK:RESET":
                    for btn in self.board_buttons:
                        btn.setText("")
                        btn.setStyleSheet("")
                        btn.setEnabled(True)
                    self.game_active = True
                    if self.mode_combo.currentText() == 'AI vs AI':
                        self.ai_timer.start(100)
            except:
                self.handle_disconnection()
        else:
            for btn in self.board_buttons:
                btn.setText("")
                btn.setStyleSheet("")
            self.game_active = True

    def closeEvent(self, event):
        try:
            if self.serial_conn:
                self.serial_conn.close()

            # Save settings
            self.config['Serial']['baud_rate'] = self.baud_combo.currentText()
            self.config['Game']['default_mode'] = self.mode_combo.currentText()
            with open('tictactoe.ini', 'w') as f:
                self.config.write(f)

            if event:  # Перевіряємо, чи event не None
                event.accept()
        except Exception as e:
            print(f"Error during closing: {e}")
            if event:
                event.accept()


if __name__ == '__main__':
    try:
        app = QApplication(sys.argv)
        app.setStyle('Fusion')
        window = TicTacToeGUI()
        window.show()
        sys.exit(app.exec_())
    except KeyboardInterrupt:
        print("\nProgram finished correctly")
        sys.exit(0)