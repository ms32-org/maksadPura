from webbrowser import open
from elevate import elevate
import ctypes
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception as e:
        return False

open("https://google.com") if not is_admin() else open("https://youtube.com")