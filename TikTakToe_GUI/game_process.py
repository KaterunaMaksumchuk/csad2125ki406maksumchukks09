from constants import MODE_MAP, MARKER_X, MARKER_O, MARKER_EMPTY

class GameProcess:
    def __init__(self, serial_manager):
        self.serial_manager = serial_manager
        self.game_active = True
        self.current_mode = MODE_MAP['Man vs Man']

    def set_mode(self, mode):
        """Set game mode and send to device."""
        if not self.serial_manager.is_connected():
            raise ConnectionError("Not connected to device")

        mode_value = MODE_MAP[mode]
        self.serial_manager.send_command(f"MODE{mode_value}")
        response = self.serial_manager.read_response()
        
        if response == "OK:MODE_SET":
            self.current_mode = mode_value
            self.game_active = True
            return True
        return False

    def make_move(self, position):
        """Make a move in the game."""
        if not self.serial_manager.is_connected():
            raise ConnectionError("Not connected to device")

        if not self.game_active:
            return None

        self.serial_manager.send_command(f"MOVE{position}")
        return self.process_response()

    def process_response(self):
        """Process response from the device."""
        response = self.serial_manager.read_response()
        if not response:
            return None

        result = {
            'board_state': None,
            'game_over': False,
            'winner': None,
            'draw': False,
            'error': None
        }

        if response.startswith("BOARD:"):
            parts = response.split(":")
            result['board_state'] = self._parse_board_state(parts[1])

            if "WIN" in response:
                result['game_over'] = True
                result['winner'] = MARKER_X if parts[3] == "1" else MARKER_O
                self.game_active = False
            elif "DRAW" in response:
                result['game_over'] = True
                result['draw'] = True
                self.game_active = False

        elif response.startswith("ERR:"):
            result['error'] = response[4:]

        return result

    def _parse_board_state(self, state_str):
        """Parse board state string into list of markers."""
        board_state = []
        for char in state_str:
            if char == "0":
                board_state.append(MARKER_EMPTY)
            elif char == "1":
                board_state.append(MARKER_X)
            else:
                board_state.append(MARKER_O)
        return board_state

    def reset_game(self):
        """Reset game state."""
        self.game_active = True