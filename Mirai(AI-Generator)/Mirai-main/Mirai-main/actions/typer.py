import pyautogui
import time

class Typer:
    def __init__(self):
        pyautogui.PAUSE = 0.05
        
    def type_text(self, text, interval=0.05):
        try:
            time.sleep(0.5)
            pyautogui.typewrite(text, interval=interval)
            return True
        except Exception as e:
            print(f"  ❌ Erro ao digitar: {e}")
            return False
    
    def press_key(self, key):
        try:
            pyautogui.press(key)
            return True
        except Exception as e:
            print(f"  ❌ Erro ao pressionar {key}: {e}")
            return False
    
    def hotkey(self, *keys):
        try:
            pyautogui.hotkey(*keys)
            return True
        except Exception as e:
            print(f"  ❌ Erro ao pressionar atalho: {e}")
            return False