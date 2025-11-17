# coded by AI

import threading
import time
from pynput import keyboard

KEY_TO_PRESS = 'у'
INTERVAL = 0.5
TOGGLE_KEY = keyboard.Key.f6
EXIT_KEY = keyboard.Key.esc

SPECIAL_KEYS = {
    'space': keyboard.Key.space,
    'enter': keyboard.Key.enter,
    'tab': keyboard.Key.tab,
    'esc': keyboard.Key.esc,
    'shift': keyboard.Key.shift,
    'ctrl': keyboard.Key.ctrl,
    'alt': keyboard.Key.alt,
    'backspace': keyboard.Key.backspace,
    'up': keyboard.Key.up,
    'down': keyboard.Key.down,
    'left': keyboard.Key.left,
    'right': keyboard.Key.right
}

def get_key_object(key_name):
    if not isinstance(key_name, str):
        return key_name
    name = key_name.lower()
    if name in SPECIAL_KEYS:
        return SPECIAL_KEYS[name]
    return key_name

key_obj = get_key_object(KEY_TO_PRESS)

controller = keyboard.Controller()
running = False
exit_program = False

def click_loop():
    global running, exit_program
    while not exit_program:
        if running:
            try:
                controller.press(key_obj)
                controller.release(key_obj)
            except Exception as e:
                print(f"Ошибка при нажатии клавиши: {e}")
            time.sleep(INTERVAL)
        else:
            time.sleep(0.05)

def on_press(key):
    global running, exit_program
    try:
        if key == TOGGLE_KEY:
            running = not running
            status = "ВКЛЮЧЕН" if running else "ВЫКЛЮЧЕН"
            print(f"[Toggle] Автокликер {status} (нажатие: {KEY_TO_PRESS}, интервал: {INTERVAL}s)")
        elif key == EXIT_KEY:
            exit_program = True
            print("Выход...")
            return False
    except Exception as e:
        print(f"Listener error: {e}")

if __name__ == "__main__":
    print("Автокликер запущен.")
    print(f"Нажмите {TOGGLE_KEY} чтобы вкл/выкл, {EXIT_KEY} чтобы выйти.")
    worker = threading.Thread(target=click_loop, daemon=True)
    worker.start()

    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()

    exit_program = True
    worker.join(timeout=1.0)
    print("Завершено.")
