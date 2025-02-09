import pyautogui
import threading
import time

class CursorManager:
    def __init__(self, hide_after_seconds=3):
        self.hide_after_seconds = hide_after_seconds
        self.last_move_time = time.time()
        self.is_hidden = False
        self._monitor_thread = None
        self._running = False

    def start_monitoring(self):
        if self._monitor_thread is None:
            self._running = True
            self._monitor_thread = threading.Thread(target=self._monitor_cursor)
            self._monitor_thread.daemon = True
            self._monitor_thread.start()

    def stop_monitoring(self):
        self._running = False
        if self._monitor_thread:
            self._monitor_thread.join()
            self._monitor_thread = None

    def _monitor_cursor(self):
        last_pos = pyautogui.position()
        
        while self._running:
            current_pos = pyautogui.position()
            
            if current_pos != last_pos:
                self.last_move_time = time.time()
                last_pos = current_pos
                if self.is_hidden:
                    self.show_cursor()
            elif not self.is_hidden and (time.time() - self.last_move_time) > self.hide_after_seconds:
                self.hide_cursor()
            
            time.sleep(0.1)  # Check every 100ms

    def hide_cursor(self):
        if not self.is_hidden:
            pyautogui.FAILSAFE = False
            current_x, current_y = pyautogui.position()
            # Move cursor to bottom-right corner
            pyautogui.moveTo(719, 719)
            self.is_hidden = True
            pyautogui.FAILSAFE = True

    def show_cursor(self):
        if self.is_hidden:
            pyautogui.FAILSAFE = False
            # Move cursor back to center
            pyautogui.moveTo(360, 360)
            self.is_hidden = False
            pyautogui.FAILSAFE = True
