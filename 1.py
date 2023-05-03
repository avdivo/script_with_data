import tkinter as tk
from tkinter import ttk
from threading import Thread
import time


class MainApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Main App")

        self.start_button = ttk.Button(self.master, text="Start", command=self.start_thread)
        self.start_button.pack(padx=10, pady=10)

        self.message_count = 0
        self.stop_event = False

    def start_thread(self):
        thread = Thread(target=self.thread_function)
        thread.start()

    def thread_function(self):
        while not self.stop_event:
            self.message_count += 1
            print(f"Message {self.message_count}")
            time.sleep(3)
            if self.message_count == 3:
                self.stop_event = True
                self.open_modal()

    def open_modal(self):
        modal_window = tk.Toplevel(self.master)
        modal_window.title("Modal Window")

        modal_label = ttk.Label(modal_window, text="Messages stopped")
        modal_label.pack(padx=10, pady=10)

        ok_button = ttk.Button(modal_window, text="OK", command=self.close_modal)
        ok_button.pack(padx=10, pady=10)

        modal_window.grab_set()

    def close_modal(self):
        self.master.focus_set()
        self.master.grab_set()
        self.master.lift()
        self.master.focus_force()
        self.master.grab_release()

if __name__ == "__main__":
    root = tk.Tk()
    app = MainApp(root)
    root.mainloop()