import os
import sys
import time
import subprocess
import ctypes
import threading

# Windows Virtual Key Codes
VK_CODES = {
    'w': 0x57, 'a': 0x41, 's': 0x53, 'd': 0x44,
    'j': 0x4A, 'k': 0x4B, 'l': 0x4C, 'i': 0x49, 'u': 0x55,
    'lshift': 0xA0, 'space': 0x20, 'enter': 0x0D, 'escape': 0x1B,
    'up': 0x26, 'down': 0x28, 'left': 0x25, 'right': 0x27,
    'num1': 0x61, 'num2': 0x62, 'num3': 0x63, 'num0': 0x60,
    '1': 0x31, '2': 0x32, '3': 0x33, '0': 0x30
}

KEYEVENTF_KEYUP = 0x0002

def press_key(key):
    try:
        code = VK_CODES.get(key.lower())
        if code and sys.platform == 'win32':
            ctypes.windll.user32.keybd_event(code, 0, 0, 0)
    except Exception as e:
        print(f"[KeyInputError] {e}")

def release_key(key):
    try:
        code = VK_CODES.get(key.lower())
        if code and sys.platform == 'win32':
            ctypes.windll.user32.keybd_event(code, 0, KEYEVENTF_KEYUP, 0)
    except Exception as e:
        print(f"[KeyInputError] {e}")

class GolazoGameBridge:
    def __init__(self, exe_path=r"D:\Golazo! Football League\GolazoPlugInDigital.exe"):
        self.exe_path = exe_path
        self.process = None
        self.active_keys = set()
        self.lock = threading.Lock()

    def launch_game(self):
        if os.path.exists(self.exe_path):
            try:
                if self.process is None or self.process.poll() is not None:
                    print(f"[GolazoBridge] Launching Unity Game: {self.exe_path}")
                    self.process = subprocess.Popen([self.exe_path], cwd=os.path.dirname(self.exe_path))
                    return True
            except Exception as e:
                print(f"[GolazoBridge] Error launching game: {e}")
        else:
            print(f"[GolazoBridge] Game executable not found at {self.exe_path}")
        return False

    def close_game(self):
        if self.process and self.process.poll() is None:
            print("[GolazoBridge] Terminating Unity Game")
            self.process.terminate()
            self.process = None

    def handle_player_input(self, player_index, input_data):
        """
        player_index: 0 for Player 1 (Red/Left), 1 for Player 2 (Blue/Right)
        input_data: dict with moveX, moveY, pass, shoot, tackle, sprint, throughPass
        """
        move_x = input_data.get('moveX', 0)
        move_y = input_data.get('moveY', 0)
        is_pass = input_data.get('pass', False)
        is_shoot = input_data.get('shoot', False)
        is_tackle = input_data.get('tackle', False)
        is_sprint = input_data.get('sprint', False)
        is_through = input_data.get('throughPass', False)

        with self.lock:
            if player_index == 0:
                # Player 1 Mapping (WASD + J/K/L/I/Shift)
                up_key, down_key, left_key, right_key = 'w', 's', 'a', 'd'
                pass_k, shoot_k, tackle_k, sprint_k, through_k = 'j', 'k', 'l', 'lshift', 'i'
            else:
                # Player 2 Mapping (Arrow Keys + 1/2/3/0/U)
                up_key, down_key, left_key, right_key = 'up', 'down', 'left', 'right'
                pass_k, shoot_k, tackle_k, sprint_k, through_k = '1', '2', '3', '0', 'u'

            # Directional Inputs
            self._set_key_state(left_key, move_x < -0.3)
            self._set_key_state(right_key, move_x > 0.3)
            self._set_key_state(up_key, move_y < -0.3)
            self._set_key_state(down_key, move_y > 0.3)

            # Action Inputs
            self._set_key_state(pass_k, is_pass)
            self._set_key_state(shoot_k, is_shoot)
            self._set_key_state(tackle_k, is_tackle)
            self._set_key_state(sprint_k, is_sprint)
            self._set_key_state(through_k, is_through)

    def _set_key_state(self, key, should_be_pressed):
        if should_be_pressed and key not in self.active_keys:
            press_key(key)
            self.active_keys.add(key)
        elif not should_be_pressed and key in self.active_keys:
            release_key(key)
            self.active_keys.remove(key)

# Global Singleton Bridge
golazo_bridge_instance = GolazoGameBridge()
