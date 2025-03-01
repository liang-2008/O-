import sys
import os
import time
import threading
import tkinter as tk
from pygame import mixer
from pynput import mouse, keyboard
import pyautogui


class PrankProgram:
    def __init__(self):
        # 初始化参数
        self.original_volume = 50
        self.target_volume = 100
        self.get_resource_path()

        # 创建隐藏窗口
        self.window = self.create_hidden_window()

        # 其他初始化代码...
        self.setup_audio()
        self.safe_set_volume(self.target_volume)
        self.click_count = 0
        self.last_click_time = 0
        self.start_audio_thread()
        self.start_volume_protection()

    def create_hidden_window(self):
        root = tk.Tk()
        root.overrideredirect(1)
        root.geometry("0x0+0+0")
        return root

    def get_resource_path(self):
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))
        self.sound_path = os.path.join(base_path, "o泡果奶广告曲.wav")

    def setup_audio(self):
        mixer.init()
        self.sound = mixer.Sound(self.sound_path)
        self.sound.set_volume(1.0)
        self.playing = True

    def safe_set_volume(self, target_percent):
        target = max(0, min(100, target_percent))
        steps = int(target / 2)  # 每次音量键增加约5%
        pyautogui.press('volumeup', presses=steps)

    def start_audio_thread(self):
        self.audio_thread = threading.Thread(target=self.loop_audio)
        self.audio_thread.daemon = True
        self.audio_thread.start()

    def loop_audio(self):
        while self.playing:
            self.sound.play()
            time.sleep(self.sound.get_length())

    def on_click(self, x, y, button, pressed):
        if pressed and button == mouse.Button.left:
            current_time = time.time()
            if current_time - self.last_click_time < 1.0:
                self.click_count += 1
                if self.click_count >= 4:
                    self.clean_exit()
            else:
                self.click_count = 0
            self.last_click_time = current_time

    def clean_exit(self):
        self.playing = False
        # 先将音量调至最低
        pyautogui.press('volumedown', presses=50)
        # 等待 0.2 秒确保音量调整完成
        time.sleep(0.2)
        # 再将音量调至 30%
        pyautogui.press('volumeup', presses=15)
        mixer.quit()
        self.window.destroy()
        os._exit(0)

    def run(self):
        with mouse.Listener(on_click=self.on_click) as listener:
            self.window.mainloop()

    def on_volume_key_press(self, key):
        try:
            # 检测音量调小或静音按键
            if key.char == 'volumedown' or key.char == 'mute':
                self.safe_set_volume(self.target_volume)  # 恢复目标音量
        except AttributeError:
            pass

    def start_volume_protection(self):
        self.volume_listener = keyboard.Listener(on_press=self.on_volume_key_press)
        self.volume_listener.start()

        # 定时检查音量并恢复，适当降低检查频率
        self.volume_check_thread = threading.Thread(target=self.periodic_volume_check)
        self.volume_check_thread.daemon = True
        self.volume_check_thread.start()

    def periodic_volume_check(self):
        """ 定时检查音量并恢复到目标值，每 0.5 秒检查一次 """
        while self.playing:
            self.safe_set_volume(self.target_volume)
            time.sleep(0.2)  # 每 0.5 秒检查一次


if __name__ == "__main__":
    program = PrankProgram()
    program.run()