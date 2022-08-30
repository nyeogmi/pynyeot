import ctypes
import threading

# NOTE: Hotkey is WIN-ALT-SPACE on Windows


def log_note(value):
    with open("notes.txt", "at") as f:
        f.write(value)
        f.write("\n")


def get_note():
    from tkinter import Tk, StringVar
    from tkinter import ttk

    root = Tk()
    value = StringVar()
    frm = ttk.Frame(root)

    note = ttk.Entry(frm, textvariable=value, width=70, font=("Segoe UI", 30))
    note.grid(column=0, row=0)
    note.focus_force()

    frm.pack()

    def close(event):
        root.destroy()

    def submit(event):
        root.destroy()
        log_note(value.get())

    note.bind("<Escape>", close)
    note.bind("<Return>", submit)

    root.wm_attributes("-topmost", "True")
    root.eval("tk::PlaceWindow . center")
    root.overrideredirect(1)
    root.mainloop()


"""
def wait_linux():
    from pynput.keyboard import GlobalHotKeys

    with GlobalHotKeys({HOTKEY: get_note}) as h:
        h.join()
"""


def wait_win32():
    # source: http://timgolden.me.uk/python/win32_how_do_i/catch_system_wide_hotkeys.html
    from ctypes import wintypes
    import win32con

    byref = ctypes.byref
    user32 = ctypes.windll.user32

    getting_note_lock = threading.Lock()
    getting_note = False

    def handle_hotkey():
        with getting_note_lock:
            nonlocal getting_note
            if getting_note:
                return
            getting_note = True

        def get_note_and_done():
            nonlocal getting_note
            try:
                get_note()
            finally:
                with getting_note_lock:
                    getting_note = False

        threading.Thread(target=get_note_and_done).start()

    HOTKEYS = {1: (win32con.VK_SPACE, win32con.MOD_ALT | win32con.MOD_WIN)}  # 96 = tilde
    HOTKEY_ACTIONS = {1: handle_hotkey}

    for id_, (vk, modifiers) in HOTKEYS.items():
        if not user32.RegisterHotKey(None, id_, modifiers, vk):
            raise ValueError("unable to register hotkeys: {}".format(id_))

    msg = wintypes.MSG()
    while user32.GetMessageA(byref(msg), None, 0, 0) != 0:
        if msg.message == win32con.WM_HOTKEY:
            action = HOTKEY_ACTIONS.get(msg.wParam)
            if action:
                action()

        user32.TranslateMessage(byref(msg))
        user32.DispatchMessageA(byref(msg))


if __name__ == "__main__":
    wait_win32()